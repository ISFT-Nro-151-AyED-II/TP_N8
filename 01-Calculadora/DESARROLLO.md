# Desarrollo TP N°8 - Ejercicio 3.1: Calculadora Simple utilizando Tkinter

---

## 📂 Estructura del Proyecto

Para garantizar la escalabilidad y mantener el código ordenado, se aplicó la siguiente jerarquía de directorios, separando la lógica de negocio de la interfaz gráfica:

```text
01-Calculadora/
│
├── Main.py                  -> Punto de entrada de la aplicación.
├── core/
│   ├── __init__.py          -> Inicializador del módulo core.
│   └── Matematica.py        -> Aislamiento de la lógica de negocio (matemática).
├── ui/
│   ├── __init__.py          -> Inicializador del módulo ui.
│   └── Ventana.py           -> Gestión exclusiva de la vista (Tkinter).
└── img/
    └── imagen.png           -> Recursos estáticos (fondo).

```
---

## 💡 Enfoque técnico: Ejercicio 3.1 (Calculadora)

**Arquitectura y Modularización:**
Se optó por una arquitectura de separación de responsabilidades (Separation of Concerns). Se dividió el proyecto en dos capas principales:

1. **Capa de Presentación (`ui/`):** Gestiona exclusivamente la instanciación de Tkinter, el diseño espacial (resolución estricta de 600x400 píxeles), el centrado dinámico del contenedor y la carga de recursos gráficos estáticos (`imagen.png`).

2. **Capa de Lógica de Negocio (`core/`):** Aislada de la GUI, responsable de procesar el cálculo matemático de forma independiente.

**Decisiones Algorítmicas:**

* **Evaluación de Expresiones:** Se utilizó `eval()` de Python por su alta eficiencia al resolver expresiones aritméticas en cadena. Sin embargo, para mitigar los riesgos críticos de seguridad (ej. inyección de código) inherentes a esta función, se implementó una validación estricta por Expresiones Regulares (`re.match`), asegurando que el input se limite exclusivamente a dígitos y operadores matemáticos.

* **Gestión de Errores (Defensive Programming):** El bloque lógico incluye manejo de excepciones nativo (`ZeroDivisionError`, `SyntaxError`) para capturar y neutralizar intentos de dividir por cero o procesar expresiones mal formadas (ej: `5++5`). Esto delega a la vista mensajes de error claros ("Error: Div por cero") sin comprometer la estabilidad del proceso principal.

* **Tolerancia a fallos en UI:** La carga de la imagen de fondo se envuelve en un bloque `try...except`. Si el archivo `imagen.png` es eliminado, movido o está corrupto, la UI implementa un fallback dinámico a un fondo de color sólido, garantizando la disponibilidad ininterrumpida de la aplicación.

---

## 🖥️ Simulación de Ejecución (Capa Lógica)

La siguiente simulación demuestra la robustez del componente lógico ante diferentes inputs generados desde la interfaz de usuario:

```text
Input UI                    ->  Llamada Interna              -> Output / UI Update

[5][.][2][+][5][.][3][=]    ->  evaluate("5.2+5.3")          -> "10.5"
[1][0][/][0][=]             ->  evaluate("10/0")             -> "Error: Div por cero"
[9][*][/][3][=]             ->  evaluate("9*/3")             -> "Error: Sintaxis"
[2][.][5][*][2][=]          ->  evaluate("2.5*2")            -> "5.0" -> "5" (Formateo)
```