import tkinter as tk
from tkinter import ttk, messagebox
from core.GestorPedidos import GestorPedidos

class PanelPrincipal:
    def __init__(self, master: tk.Toplevel, gestor_pedidos: GestorPedidos):
        # La vista no sabe nada de SQLite, solo dialoga con el Gestor de Pedidos.
        self.master = master
        self.gestor_pedidos = gestor_pedidos
        
        self.master.title("REPAIR CENTER - Panel de Gestión")
        self.master.geometry("600x400")
        self.master.resizable(False, False)
        
        # Uso de StringVar para capturar datos. La validación de tipos (ej: altura entera)
        # se delega al gestor del core para no acoplar lógica de negocio acá.
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_calle = tk.StringVar()
        self.var_altura = tk.StringVar()
        self.var_inconveniente = tk.StringVar()
        self.var_tecnico = tk.StringVar()
        self.var_fecha = tk.StringVar()
        
        self._construir_ui()
        # Sincronización inicial de la vista con la base de datos.
        self._refrescar_tabla()

    def _construir_ui(self):
        # Geometría estricta para encajar en 600x400.
        # LabelFrame izquierdo: Formulario (ancho 260px).
        marco_izq = tk.LabelFrame(self.master, text=" Nuevo Pedido ", padx=5, pady=5)
        marco_izq.place(x=10, y=10, width=260, height=370)
        
        # LabelFrame derecho: Grilla de base de datos (ancho 310px)
        marco_der = tk.LabelFrame(self.master, text=" Tickets Activos ", padx=5, pady=5)
        marco_der.place(x=280, y=10, width=310, height=370)

        self._armar_formulario(marco_izq)
        self._armar_grilla(marco_der)

    def _armar_formulario(self, contenedor):
        # Mapeo dinámico para no repetir código de renderizado tk.Label/tk.Entry.
        campos = [
            ("Nombre:", self.var_nombre, False),
            ("Apellido:", self.var_apellido, False),
            ("Calle:", self.var_calle, False),
            ("Altura:", self.var_altura, False),
            ("Falla:", self.var_inconveniente, False),
            ("Técnico:", self.var_tecnico, True),
            ("Fecha/Hora:", self.var_fecha, True)
        ]

        for i, (label_text, var, opcional) in enumerate(campos):
            texto_final = f"{label_text}" if not opcional else f"{label_text} *"
            tk.Label(contenedor, text=texto_final).grid(row=i, column=0, sticky="w", pady=4)
            # Aplicación de estética sunken (hundido) y bd=2.
            tk.Entry(
                contenedor, 
                textvariable=var, 
                relief="sunken", 
                bd=2, 
                width=20
            ).grid(row=i, column=1, pady=4, padx=5)

        tk.Label(
            contenedor, text="* Campos opcionales iniciales", font=("Arial", 8, "italic")
        ).grid(row=len(campos), column=0, columnspan=2, pady=(10, 5))

        # Botón con relieve responsivo alineado a la estética del Login.
        self.btn_registrar = tk.Button(
            contenedor, 
            text="Registrar Ticket", 
            relief="raised", 
            bd=3, 
            command=self.procesar_registro,
            cursor="hand2"
        )
        self.btn_registrar.grid(row=len(campos)+1, column=0, columnspan=2, pady=5, sticky="ew", padx=10)
        
        # Bindings para el feedback táctil visual.
        self.btn_registrar.bind("<ButtonPress-1>", lambda e: self.btn_registrar.config(relief="sunken"))
        self.btn_registrar.bind("<ButtonRelease-1>", lambda e: self.btn_registrar.config(relief="raised"))

    def _armar_grilla(self, contenedor):
        columnas = ("id", "cliente", "tecnico")
        self.tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=15)
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("cliente", text="Cliente")
        self.tabla.heading("tecnico", text="Técnico")
        
        # Ajuste milimétrico de columnas para no desbordar los 310px del marco derecho.
        self.tabla.column("id", width=30, anchor="center")
        self.tabla.column("cliente", width=120, anchor="w")
        self.tabla.column("tecnico", width=120, anchor="w")
        
        scroll = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def procesar_registro(self):
        # Desacoplamiento: Pasamos los strings al gestor.
        # Él evalúa, convierte tipos y golpea la base de datos.
        exito, mensaje = self.gestor_pedidos.registrar_pedido(
            self.var_nombre.get(),
            self.var_apellido.get(),
            self.var_calle.get(),
            self.var_altura.get(),
            self.var_inconveniente.get(),
            self.var_tecnico.get(),
            self.var_fecha.get()
        )

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self._limpiar_formulario()
            self._refrescar_tabla()
        else:
            messagebox.showwarning("Aviso de Validación", mensaje)

    def _limpiar_formulario(self):
        for var in (self.var_nombre, self.var_apellido, self.var_calle, self.var_altura, 
                    self.var_inconveniente, self.var_tecnico, self.var_fecha):
            var.set("")

    def _refrescar_tabla(self):
        # Destrucción de nodos actuales en el Treeview para evitar duplicados.
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Fetching a SQLite. Recordá la tupla del SELECT en GestorPedidos:
        # (id_ticket, nombre, apellido, inconveniente, tecnico, fecha_hora, estado)
        pedidos = self.gestor_pedidos.obtener_todos_los_pedidos()
        
        for p in pedidos:
            id_ticket = p[0]
            # Algoritmo de formato rápido para ahorrar espacio en grilla: J. Pérez.
            inicial_nombre = p[1][0].upper() if p[1] else ""
            apellido = p[2].capitalize()
            cliente_formateado = f"{inicial_nombre}. {apellido}"
            tecnico = p[4]
            
            self.tabla.insert("", "end", values=(id_ticket, cliente_formateado, tecnico))