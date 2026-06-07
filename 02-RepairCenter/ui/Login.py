import tkinter as tk
from tkinter import messagebox
from core.Autenticacion import Autenticacion
from core.GestorPedidos import GestorPedidos

# Importación diferida para evitar referencias circulares antes de tiempo.
# Asumimos que PanelPrincipal.py va a existir en el próximo paso.
from ui.PanelPrincipal import PanelPrincipal

class Login:
    def __init__(self, master: tk.Tk, gestor_auth: Autenticacion, gestor_pedidos: GestorPedidos):
        # El Login recibe las dos dependencias lógicas:
        # 1. Para usarse a sí mismo (gestor_auth).
        # 2. Para pasárselo al panel si el login es exitoso (gestor_pedidos).
        self.master = master
        self.gestor_auth = gestor_auth
        self.gestor_pedidos = gestor_pedidos
        
        self.master.title("REPAIR CENTER - Login")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        
        self.var_usuario = tk.StringVar()
        self.var_password = tk.StringVar()
        
        self._configurar_fondo()
        self._construir_ui()

    def _configurar_fondo(self):
        try:
            # Carga de la imagen original (600x400).
            img_original = tk.PhotoImage(file="img/imagen.png")
            # Reducción de escala a la mitad exacta (300x200) nativa de Tkinter.
            self.bg_img = img_original.subsample(2, 2)
            fondo = tk.Label(self.master, image=self.bg_img)
            fondo.place(x=0, y=0, relwidth=1, relheight=1)
        except tk.TclError:
            self.master.configure(bg="#2c3e50")
            print("[UI] Advertencia: No se pudo cargar img/imagen.png. Usando color sólido.")

    def _construir_ui(self):
        # Marco central para contener los widgets sobre la imagen.
        marco = tk.Frame(self.master, bd=2, relief="groove", padx=10, pady=10)
        marco.place(relx=0.5, rely=0.5, anchor="center", width=220, height=150)
        
        # Labels e inputs. El relief="sunken" y bd=2 (border width) genera el efecto hundido.
        tk.Label(marco, text="Usuario:").pack(pady=(5, 0))
        tk.Entry(marco, textvariable=self.var_usuario, relief="sunken", bd=2).pack()
        
        tk.Label(marco, text="Contraseña:").pack(pady=(5, 0))
        # show="*" enmascara la contraseña por estándar de seguridad visual.
        tk.Entry(marco, textvariable=self.var_password, show="*", relief="sunken", bd=2).pack()
        
        # Botón responsivo: relief="raised" (elevado) con bd=3 para volumen.
        self.btn_ingresar = tk.Button(
            marco, 
            text="Ingresar", 
            relief="raised", 
            bd=3, 
            command=self.procesar_login, 
            cursor="hand2"
        )
        self.btn_ingresar.pack(pady=10)
        
        # Bindings explícitos para forzar el hundimiento visual ("sunken") al presionar el clic izquierdo
        # y restaurarlo a "raised" al soltarlo, dándole feedback táctil.
        self.btn_ingresar.bind("<ButtonPress-1>", lambda e: self.btn_ingresar.config(relief="sunken"))
        self.btn_ingresar.bind("<ButtonRelease-1>", lambda e: self.btn_ingresar.config(relief="raised"))

    def procesar_login(self):
        usr = self.var_usuario.get()
        pwd = self.var_password.get()
        
        if self.gestor_auth.validar_credenciales(usr, pwd):
            self._abrir_panel_principal()
        else:
            messagebox.showerror("Error de Acceso", "Credenciales incorrectas o campos vacíos.")

    def _abrir_panel_principal(self):
        # Ocultamos el login sin matar el mainloop.
        self.master.withdraw()
        
        # Creamos la ventana hija dependiente del master invisible.
        ventana_secundaria = tk.Toplevel(self.master)
        
        # Regla de oro de arquitectura Tkinter:
        # Si el usuario cierra el Panel Principal dándole a la 'X',
        # capturamos ese evento y destruimos el master original para liberar la memoria y cerrar la app.
        ventana_secundaria.protocol("WM_DELETE_WINDOW", self.master.destroy)
        
        # Instanciamos la UI principal inyectándole el gestor de base de datos.
        PanelPrincipal(ventana_secundaria, self.gestor_pedidos)