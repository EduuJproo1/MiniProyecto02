import tkinter as tk
from gui import AplicacionGenerador

if __name__ == "__main__":
    # Ventana raíz
    root = tk.Tk()
    # Clase de la interfaz
    app = AplicacionGenerador(root)
    # Bucle principal de ejecución
    root.mainloop()