# Trabajo Práctico N°8 - Resolución Ejercicio 3.2 y 3.3: Repair Center

---

## 📂 Estructura del Proyecto

Se implementó una arquitectura multicapa (Presentación, Lógica de Negocio y Datos) para aislar las responsabilidades y permitir la escalabilidad del sistema. La estructura final de directorios y archivos es la siguiente:

```text
02-RepairCenter/
│
├── core/
│   ├── __init__.py
│   ├── BaseDatos.py       (Capa de datos: Conexión a SQLite y DDL)
│   ├── Autenticacion.py   (Capa lógica: Validación de usuarios)
│   └── GestorPedidos.py   (Capa lógica: Reglas de negocio y CRUD de tickets)
│
├── ui/
│   ├── __init__.py
│   ├── Login.py           (Capa de presentación: Pantalla de inicio de sesión)
│   └── PanelPrincipal.py  (Capa de presentación: Gestión de pedidos)
│
├── db/                    (Directorio de persistencia para repair_center.db)
│
├── img/
│   └── imagen.png         (Recurso visual para el fondo de la interfaz)
│
├── Main.py                (Punto de entrada e inyección de dependencias)
└── DESARROLLO.md          (Documentación técnica del enfoque algorítmico)

```
---

## 💡 Enfoque Técnico: Capa de Acceso a Datos (`BaseDatos.py`)

Para el manejo de persistencia se implementó el patrón *Repository* simplificado. Se creó una clase `BaseDatos` que centraliza absolutamente todas las operaciones de entrada/salida a SQLite.

1.  **Programación Defensiva en Rutas:** El método `_asegurar_directorio()` utiliza la librería `os` para verificar y crear el directorio `/db` en tiempo de ejecución. Esto previene un crash de la aplicación si el repositorio es clonado sin la carpeta de base de datos.

2.  **Prevención de Deadlocks (Hilos):** Al inicializar la conexión con `sqlite3.connect()`, se seteó el parámetro `check_same_thread=False`. Tkinter corre en su propio *event loop* y puede disparar eventos desde hilos que SQLite bloquearía por defecto, generando cuelgues en la UI.
   
3.  **Parametrización de Consultas:** Los métodos `ejecutar_escritura` y `ejecutar_lectura` exigen el uso de tuplas para inyectar datos (`parametros`). Esto previene ataques de Inyección SQL y delega el escapado de caracteres a la librería nativa de Python.
   
4.  **Auto-Seeding:** El método `inicializar_tablas()` no solo crea el esquema relacional (`usuarios` y `pedidos`), sino que verifica si existe el usuario `admin`. Si no existe, lo inserta por defecto (admin / 1234) para garantizar que el evaluador pueda testear el módulo de Login sin necesidad de inyectar datos a mano en el motor SQLite.

## 🛠️ Simulación de Ejecución (Consola Interna - Capa Datos)

**Caso 1: Primer arranque de la aplicación (Base de datos inexistente)**
* **Acción:** Instanciación de `db = BaseDatos()` y llamada a `db.inicializar_tablas()`.

* **Procesamiento:** `_asegurar_directorio()` crea la carpeta `db/`. SQLite crea el archivo `repair_center.db`. Se ejecutan los `CREATE TABLE`. Se inserta el usuario 'admin'.

* **Salida / Estado:** El archivo físico pesa ~12KB. Operación silenciosa (sin errores).

**Caso 2: Inserción con error de integridad (Constraint de unicidad)**
* **Acción interna:** Intento de registrar un usuario duplicado (`INSERT INTO usuarios (usuario...) VALUES ('admin'...)`).

* **Procesamiento:** SQLite lanza excepción `IntegrityError` por el constraint `UNIQUE` en la columna `usuario`.

* **Salida Consola:** `[ERROR SQL - Escritura] UNIQUE constraint failed: usuarios.usuario` (La app no crashea, la clase captura y reporta el error).

---

## 💡 Enfoque Técnico: Lógica de Autenticación (`Autenticacion.py`)

Para aislar el dominio de negocio (seguridad/login) del acceso a datos físico, se creó un módulo dedicado que actúa como puente lógico entre la UI y SQLite.

1.  **Inyección de Dependencias (DI):** El constructor de `Autenticacion` exige recibir un objeto del tipo `BaseDatos`. Esto centraliza el pool de conexiones en la capa superior (`Main.py`) y evita que se generen múltiples archivos `.db` bloqueados en paralelo.

2.  **Patrón Fail-Fast:** Antes de ejecutar la consulta SQL, el método `validar_credenciales` evalúa si los strings de entrada están vacíos o son nulos. Si lo son, retorna `False` inmediatamente (Cortocircuito lógico), ahorrando el overhead de armar la consulta y golpear el motor SQLite por red o disco.
   
3.  **Sanitización de Input:** Se implementó `strip()` en los inputs para mitigar el error común de usuario donde un espacio residual al final del texto causa un rechazo de credenciales.
   
4.  **Deuda Técnica Asumida (Security):** Para mantener la simplicidad exigida en el Trabajo Práctico, las contraseñas se comparan en texto plano. En un sistema en producción, esto violaría estándares de seguridad (CWE-256). La capa debería comparar contra un hash iterado (ej: SHA-256 con Salt o Bcrypt).

## 🛠️ Simulación de Ejecución (Consola Interna - Capa Auth)

**Caso 1: Login Exitoso**
* **Input UI:** Usuario: `"admin"`, Password: `"1234"`

* **Procesamiento:** `Autenticacion.validar_credenciales("admin", "1234")`

* **Capa Datos:** Ejecuta `SELECT id FROM usuarios WHERE usuario = 'admin' AND password = '1234'`

* **Retorno:** `True` (El sistema habilita el Panel Principal).

**Caso 2: Login con espacios accidentales**
* **Input UI:** Usuario: `" admin "`, Password: `"1234 "`

* **Procesamiento:** La clase sanitiza a `"admin"` y `"1234"`.
  
* **Retorno:** `True`.

**Caso 3: Credenciales Inválidas**
* **Input UI:** Usuario: `"operador"`, Password: `"admin"`

* **Procesamiento:** La query devuelve una lista vacía `[]`.

* **Retorno:** `False` (La UI deberá mostrar un mensaje de error).

**Caso 4: Input Vacío**
* **Input UI:** Usuario: `""`, Password: `"1234"`

* **Procesamiento:** El método corta la ejecución en el primer `if` (Fail-Fast). La BD no se toca.
  
* **Retorno:** `False`.

---

## 💡 Enfoque Técnico: Lógica de Negocio (`GestorPedidos.py`)

Esta clase encapsula la manipulación de la entidad `Pedido`. Se diseñó como un intermediario estricto que protege a la base de datos de datos corruptos generados por la interfaz gráfica.

1.  **Validación en Capa Lógica:** En lugar de dejar que SQLite lance un error de tipo (Type Error) si el usuario ingresa "S/N" en el campo de altura, se captura la excepción `ValueError` mediante un bloque `try...except` en Python. Esto es más eficiente a nivel de procesamiento y permite devolver un error amigable a la capa visual.
   
2.  **Retorno de Tuplas `(bool, str)`:** Para mantener a Tkinter ciego sobre cómo operan las reglas de negocio, el método `registrar_pedido` devuelve un booleano y un string. El booleano le dice a la UI si debe limpiar el formulario o no, y el string le provee el texto exacto a inyectar en el `messagebox`, sin que la UI tenga que evaluar la lógica.
   
3.  **Tolerancia a la Omisión:** Se entiende por el flujo lógico de un Repair Center que un ticket puede ingresar *antes* de tener un técnico asignado o una fecha pactada (Incisos 3.2.4 y 3.2.5). Por ello, si la UI envía estos campos vacíos, el algoritmo los sanitiza inyectando los estados "Sin asignar" y "Sin agendar", permitiendo que el ticket persista bajo el estado 'Pendiente' para una futura actualización.

## 🛠️ Simulación de Ejecución (Consola Interna - Capa Gestor)

**Caso 1: Registro completo y correcto**
* **Input:** `registrar_pedido("Juan", "Pérez", "Av. Colón", "2050", "Pantalla rota", "Carlos", "Mañana 10hs")`

* **Validación:** Supera control de nulos. Pasa casting de `2050` a entero.

* **Retorno:** `(True, "Pedido registrado exitosamente.")`

**Caso 2: Violación de integridad lógica (Letras en altura)**
* **Input:** `registrar_pedido("Juan", "Pérez", "Av. Colón", "Mil", "Falla disco", "", "")`

* **Validación:** El casting `int("Mil")` dispara `ValueError`. 

* **Retorno:** `(False, "La altura del domicilio debe contener solo números.")` (La ejecución se aborta, no hay I/O de base de datos).

**Caso 3: Faltante de dato crítico**
* **Input:** `registrar_pedido("", "Pérez", "Av. Colón", "2050", "No enciende", "", "")`

* **Validación:** El chequeo `all([...])` detecta el string vacío en `nombre`.

* **Retorno:** `(False, "Faltan completar campos obligatorios del cliente o el inconveniente.")`

---

## 💡 Enfoque Técnico: UI - Pantalla de Login (`Login.py`)

Esta clase es la responsable de la barrera de seguridad de la aplicación (Punto 3.3). Se diseñó priorizando el aislamiento de capas y la gestión limpia de memoria en Tkinter.

1.  **Manipulación Dinámica de Imágenes:** Para cumplir con el requerimiento de una ventana de 300x200 píxeles usando una imagen original de 600x400 sin distorsionarla, se utilizó el método algorítmico `subsample(2, 2)` de la clase `PhotoImage`. Esto mapea los píxeles reduciendo su densidad a la mitad de forma nativa, evitando acoplar la aplicación a dependencias de procesamiento de imágenes de terceros (como Pillow).

2.  **Estética Funcional y UX (User Experience):** * Se aplicaron parámetros de relieve (`relief="sunken"`, `bd=2`) en los campos de entrada de datos (`Entry`) para dar profundidad visual.

    * Para el botón de "Ingresar", se configuró un relieve inicial `raised` y se programaron dos escuchadores de eventos (`Bindings` a `<ButtonPress-1>` y `<ButtonRelease-1>`). Esto sobreescribe el comportamiento estándar para garantizar un feedback responsivo claro: el botón se hunde al presionarlo y vuelve a elevarse al soltarlo.
  
3.  **Gestión del Ciclo de Vida (Mainloop):** El Login recibe la ventana principal `tk.Tk()`. Si las credenciales son válidas, **no destruye la ventana**, sino que usa el método `withdraw()` para volverla invisible y ceder el foco al `PanelPrincipal` instanciado como `Toplevel`. Además, se mapeó el evento de cierre de la ventana secundaria (`WM_DELETE_WINDOW`) para destruir el `master` oculto, garantizando que el proceso de Python finalice limpiamente y no quede corriendo como un hilo huérfano en segundo plano.

---

## 💡 Enfoque Técnico: UI - Panel Principal (`PanelPrincipal.py`)

Esta clase orquesta la vista principal donde el operador registra los tickets (Punto 3.2 y sub-incisos). Se adoptó un patrón arquitectónico *Master-Detail* adaptado a una única ventana fija de 600x400 px.

1.  **Restricción Geométrica Absoluta:** Debido a las dimensiones estrictas, no era viable utilizar el gestor de geometría `pack()` de Tkinter, ya que colapsaría el diseño en resoluciones extrañas. Se empleó `place(x, y, width, height)` para anclar dos contenedores (`LabelFrame`): uno a la izquierda de 260px para el formulario, y uno a la derecha de 310px para la visualización de datos, asegurando una estética simétrica e irrompible.

2.  **Iteración de Renderizado (DRY):** En lugar de escribir 14 líneas de código repetitivo para generar 7 pares de `tk.Label` y `tk.Entry`, se estructuró una lista de tuplas con los atributos de cada campo y se renderizaron en un bucle `for` usando `grid()`. Esto simplifica la lectura del código y reduce la carga en memoria de la UI.
   
3.  **Coherencia Estética (UI/UX):** Se mantuvo el patrón estético del Login. Entradas de texto con relieve negativo (`sunken`, `bd=2`) y botones con relieve positivo (`raised`, `bd=3`). El botón de registro incluye los mismos *bindings* nativos para reaccionar táctilmente a los clicks del mouse.

4.  **Feedback Instantáneo de I/O:** Al presionar "Registrar Ticket", la capa visual delega la petición al Core (`GestorPedidos`). Si la validación lógica y la inserción SQL son exitosas, la vista ejecuta dos acciones automáticas: invoca `_limpiar_formulario()` para acelerar la carga del siguiente cliente, y ejecuta `_refrescar_tabla()` borrando los nodos del componente `Treeview` y reconstruyéndolos con la lectura fresca de la base de datos.

---

## 💡 Enfoque Técnico: Punto de Entrada y Composición (`Main.py`)

El archivo principal no contiene lógica de negocio ni de interfaz gráfica. Su función exclusiva es orquestar el inicio del sistema.

1.  **Inversión de Control e Inyección de Dependencias (DI):** En lugar de que cada clase instancie sus propias dependencias (lo cual genera un acoplamiento rígido y dificulta el mantenimiento), `Main.py` orquesta la creación de los objetos. Primero levanta la base de datos, luego inyecta esa instancia en los gestores del *Core*, y finalmente inyecta los gestores en la capa de presentación (`Login`).
   
2.  **Manejo Global de Excepciones:** Se implementó un bloque `try...except` envolviendo la secuencia de arranque. Si ocurre un fallo catastrófico a nivel de sistema operativo (por ejemplo, denegación de permisos al intentar crear el directorio `db/`), la aplicación captura la excepción, informa el motivo exacto en la consola de texto para facilitar la depuración, y aborta el proceso de forma limpia usando `sys.exit(1)`.

## 🛠️ Simulación de Ejecución Global

**Secuencia de Inicio Exitoso:**
1. **Ejecución en consola:** `python Main.py`

2. **Salida estándar:** `[SISTEMA] Iniciando secuencia de arranque...`

3. **Acción Interna de BD:** Se crea o verifica la existencia de `db/repair_center.db`. Se inserta el usuario administrador de prueba (`admin` / `1234`).

4. **Salida estándar:** `[SISTEMA] Interfaz gráfica cargada. Esperando interacción del usuario.`

5. **Capa Visual:** Se despliega la ventana `Login` centrada, de 300x200 px, con la imagen de fondo adaptada y los controles a la espera del inicio de sesión.