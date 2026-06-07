import tkinter as tk
import sys
from core.BaseDatos import BaseDatos
from core.Autenticacion import Autenticacion
from core.GestorPedidos import GestorPedidos
from ui.Login import Login

def arrancar_sistema():
    print("[SISTEMA] Iniciando secuencia de arranque...")
    
    try:
        # 1. Composición de la capa de acceso a datos
        # Se instancia la conexión a SQLite y se garantiza la estructura de tablas.
        db = BaseDatos()
        db.inicializar_tablas()
        
        # 2. Inyección de dependencias en la capa lógica
        # Ambos gestores comparten el mismo pool de conexión a la base de datos.
        gestor_auth = Autenticacion(db)
        gestor_pedidos = GestorPedidos(db)
        
        # 3. Arranque del entorno gráfico (motor Tkinter)
        root = tk.Tk()
        
        # 4. Inyección en la capa de presentación
        # El Login recibe las dependencias lógicas para operar y orquestar el PanelPrincipal.
        app = Login(root, gestor_auth, gestor_pedidos)
        
        print("[SISTEMA] Interfaz gráfica cargada. Esperando interacción del usuario.")
        # Bloqueo del hilo principal: Acá la aplicación se queda escuchando eventos (clicks, teclado).
        root.mainloop()
        
    except Exception as e:
        # Barrera defensiva global: Evita que un error de infraestructura 
        # (ej: disco lleno o sin permisos para crear la carpeta db/) cierre la consola sin dejar rastro.
        print(f"[CRÍTICO] Fallo irrecuperable en el arranque del sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    arrancar_sistema()