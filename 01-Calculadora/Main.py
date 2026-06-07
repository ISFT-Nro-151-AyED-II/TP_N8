import tkinter as tk
from ui.Ventana import CalculadoraApp

def iniciar_aplicacion():
    # Instanciación del root de Tkinter y delegación a la clase de UI.
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()