import tkinter as tk
from tkinter import ttk
from core.Matematica import MotorCalculadora

class CalculadoraApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("CALCULADORA SIMPLE")
        self.master.geometry("600x400")
        self.master.resizable(False, False)
        
        self.motor = MotorCalculadora()
        self.expresion_actual = ""

        self._configurar_fondo()
        self._construir_ui()

    def _configurar_fondo(self):
        # Carga de la imagen. Tkinter requiere mantener la referencia (self.bg_img)
        # para que el Garbage Collector no la elimine de la memoria.
        try:
            self.bg_img = tk.PhotoImage(file="img/imagen.png")
            fondo = tk.Label(self.master, image=self.bg_img)
            fondo.place(x=0, y=0, relwidth=1, relheight=1)
        except tk.TclError:
            # Fallback defensivo por si el archivo imagen.png no se encuentra o es inválido.
            self.master.configure(bg="#1e1e1e")
            print("Advertencia: No se pudo cargar img/imagen.png. Usando fondo sólido.")

    def _construir_ui(self):
        # Contenedor central. Se usa 'place' para garantizar un centrado absoluto
        # sin importar el tamaño interno de la grilla de la calculadora.
        marco_central = tk.Frame(self.master, bg="#424242", bd=6, relief="raised")
        marco_central.place(relx=0.5, rely=0.5, relwidth=0.4, relheight=0.8, anchor="center")

        # Configuración de pesos de la grilla para que los botones se adapten
        # dinámicamente al nuevo tamaño reducido del marco central.
        for i in range(4):
            marco_central.columnconfigure(i, weight=1)
        for i in range(6): 
            marco_central.rowconfigure(i, weight=1)

        # Activación del motor de estilos nativo 'clam' para permitir mapeo de colores.
        estilo = ttk.Style()
        if 'clam' in estilo.theme_names():
            estilo.theme_use('clam')

        # Diseño base de los botones en tonos grises.
        estilo.configure("TButton", 
                         font=("Arial", 11, "bold"), 
                         background="#9e9e9e",       # Gris medio.
                         foreground="black", 
                         bordercolor="#616161",      # Gris oscuro para el borde.
                         relief="raised")
        
        # Mapeo de estados: Relieve responsive (se hunde y oscurece al clickear).
        estilo.map("TButton",
                   background=[("pressed", "#616161"), ("active", "#bdbdbd")],
                   relief=[("pressed", "sunken")])

        # Estilo de la pantalla (gris muy claro para contraste).
        estilo.configure("Pantalla.TEntry", 
                         font=("Arial", 14), 
                         fieldbackground="#e0e0e0", 
                         foreground="black")

        # Pantalla de visualización (Solo lectura para el usuario, operada por los botones).
        self.variable_pantalla = tk.StringVar()
        pantalla = ttk.Entry(
            marco_central, 
            textvariable=self.variable_pantalla, 
            style="Pantalla.TEntry", 
            justify="right", 
            state="readonly"
        )
        pantalla.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=5, pady=10)

        self._crear_teclado(marco_central)

    def _crear_teclado(self, contenedor):
        teclas = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('C', 4, 0), ('0', 4, 1), ('.', 4, 2), ('+', 4, 3),
            ('=', 5, 0, 4)
        ]

        for tecla in teclas:
            texto = tecla[0]
            fila = tecla[1]
            columna = tecla[2]
            columnspan = tecla[3] if len(tecla) > 3 else 1

            # El uso de lambda con default argument (t=texto) previene el problema
            # del late-binding en closures dentro de bucles en Python.
            comando = lambda t=texto: self._procesar_click(t)
            
            btn = ttk.Button(contenedor, text=texto, command=comando)
            btn.grid(row=fila, column=columna, columnspan=columnspan, sticky="nsew", padx=2, pady=2)

    def _procesar_click(self, valor: str):
        if valor == 'C':
            self.expresion_actual = ""
            self.variable_pantalla.set(self.expresion_actual)
        elif valor == '=':
            resultado = self.motor.resolver_expresion(self.expresion_actual)
            self.variable_pantalla.set(resultado)
            # Permite encadenar operaciones con el resultado, o limpiar si hubo error.
            self.expresion_actual = resultado if "Error" not in resultado else ""
        else:
            self.expresion_actual += valor
            self.variable_pantalla.set(self.expresion_actual)