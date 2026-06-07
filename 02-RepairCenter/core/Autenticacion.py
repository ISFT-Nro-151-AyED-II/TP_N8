from core.BaseDatos import BaseDatos

class Autenticacion:
    def __init__(self, db: BaseDatos):
        # Inyección de dependencia: Reutilizamos la conexión gestionada externamente.
        # Esto reduce el consumo de memoria y evita bloqueos (database is locked) en SQLite.
        self.db = db

    def validar_credenciales(self, usuario: str, password: str) -> bool:
        # Fail-fast: Validación en memoria para no consumir ciclos de I/O en la base de datos
        # si el usuario mandó campos vacíos.
        if not usuario or not password:
            return False

        # Sanitización superficial (strip) para evitar falsos negativos por un espacio al copiar/pegar.
        usuario_limpio = usuario.strip()
        password_limpia = password.strip()

        # Nota de arquitectura: En producción, ALMACENAR O COMPARAR CONTRASEÑAS EN TEXTO PLANO ES GRAVE.
        # Acá se hace por los requerimientos del TP N°8 y el mock sembrado en BaseDatos ('1234').
        # En el mundo real, se recupera el hash de la BD y se compara con bcrypt.checkpw().
        query = "SELECT id FROM usuarios WHERE usuario = ? AND password = ?"
        parametros = (usuario_limpio, password_limpia)

        try:
            resultado = self.db.ejecutar_lectura(query, parametros)
            # Si el array tiene contenido, hubo match exacto en la BD.
            return len(resultado) > 0
        except Exception as e:
            # Captura defensiva por si la capa inferior falla catastróficamente.
            print(f"[ERROR - Auth] Falló la validación de credenciales: {e}")
            return False