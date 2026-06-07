import sqlite3
from sqlite3 import Error
import os

class BaseDatos:
    def __init__(self, ruta_db="db/repair_center.db"):
        # Se define la ruta por defecto asumiendo ejecución desde Main.py en la raíz.
        self.ruta_db = ruta_db
        self._asegurar_directorio()

    def _asegurar_directorio(self):
        # Defensa de infraestructura: Si la carpeta db/ no existe, SQLite fallará al crear el archivo.
        # Por eso forzamos su creación a nivel sistema operativo.
        directorio = os.path.dirname(self.ruta_db)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

    def conectar(self):
        try:
            # check_same_thread=False es vital en apps de escritorio con Tkinter.
            # Evita bloqueos si la UI dispara consultas desde un hilo secundario (event loop).
            conexion = sqlite3.connect(self.ruta_db, check_same_thread=False)
            return conexion
        except Error as e:
            print(f"[CRÍTICO] Falla al conectar con SQLite: {e}")
            return None

    def inicializar_tablas(self):
        # Modelo relacional desnormalizado para los pedidos (según requerimiento de la consigna).
        # Se usa AUTOINCREMENT para delegar la gestión de IDs al motor de BD.
        query_usuarios = '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        '''
        
        query_pedidos = '''
            CREATE TABLE IF NOT EXISTS pedidos (
                id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                calle TEXT NOT NULL,
                altura INTEGER NOT NULL,
                inconveniente TEXT NOT NULL,
                tecnico TEXT,
                fecha_hora_visita TEXT,
                estado TEXT DEFAULT 'Pendiente'
            )
        '''
        
        self.ejecutar_escritura(query_usuarios)
        self.ejecutar_escritura(query_pedidos)
        
        # Sembrado de datos (Seeding): Para poder probar el punto 3.3 (Login),
        # inyectamos un usuario administrador si la tabla está vacía.
        usuario_admin = self.ejecutar_lectura("SELECT * FROM usuarios WHERE usuario = 'admin'")
        if not usuario_admin:
            self.ejecutar_escritura(
                "INSERT INTO usuarios (usuario, password) VALUES (?, ?)", 
                ('admin', '1234')
            )

    def ejecutar_escritura(self, query: str, parametros: tuple = ()):
        # Patrón centralizado para INSERT, UPDATE, DELETE.
        # Maneja la transacción (commit) y garantiza el cierre de la conexión.
        conexion = self.conectar()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute(query, parametros)
            conexion.commit()
            return True
        except Error as e:
            print(f"[ERROR SQL - Escritura] {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    def ejecutar_lectura(self, query: str, parametros: tuple = ()):
        # Patrón centralizado para SELECT. Retorna una lista de tuplas.
        conexion = self.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor()
            cursor.execute(query, parametros)
            return cursor.fetchall()
        except Error as e:
            print(f"[ERROR SQL - Lectura] {e}")
            return []
        finally:
            if conexion:
                conexion.close()