import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os
import datetime

# Importamos tus clases desde el archivo main.py
# Asegúrate de que tu script de lógica se llame 'main.py'
try:
    from main import GeneradorCasos, GestorPruebas
except ImportError:
    # Fallback por si el usuario copió todo en un solo archivo o cambió el nombre
    print("Error: No se pudo importar 'main.py'. Asegúrate de que el archivo existe.")

class AplicacionGenerador:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Casos de Prueba - INFO1148")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Variables de control
        self.ruta_gramatica = tk.StringVar()
        self.ruta_gramatica.set("No seleccionado")
        
        # Estilos y Colores
        bg_color = "#f0f0f0"
        self.root.configure(bg=bg_color)
        
        # --- SECCIÓN 1: CARGA DE ARCHIVO ---
        frame_archivo = tk.LabelFrame(root, text="1. Configuración de Gramática", padx=10, pady=10, bg=bg_color)
        frame_archivo.pack(fill="x", padx=10, pady=5)

        btn_cargar = tk.Button(frame_archivo, text="Seleccionar Archivo .TXT", command=self.seleccionar_archivo, bg="#ddd")
        btn_cargar.pack(side="left", padx=5)
        
        lbl_ruta = tk.Label(frame_archivo, textvariable=self.ruta_gramatica, fg="blue", bg=bg_color)
        lbl_ruta.pack(side="left", padx=5)

        # --- SECCIÓN 2: PARÁMETROS ---
        frame_config = tk.LabelFrame(root, text="2. Parámetros de Generación", padx=10, pady=10, bg=bg_color)
        frame_config.pack(fill="x", padx=10, pady=5)

        # Grid para inputs
        tk.Label(frame_config, text="Cant. Válidas:", bg=bg_color).grid(row=0, column=0, sticky="e")
        self.spin_validas = tk.Spinbox(frame_config, from_=1, to=1000, width=5)
        self.spin_validas.delete(0, "end")
        self.spin_validas.insert(0, 50) # Valor default
        self.spin_validas.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_config, text="Cant. Inválidas:", bg=bg_color).grid(row=0, column=2, sticky="e")
        self.spin_invalidas = tk.Spinbox(frame_config, from_=1, to=1000, width=5)
        self.spin_invalidas.delete(0, "end")
        self.spin_invalidas.insert(0, 20)
        self.spin_invalidas.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_config, text="Cant. Extremas:", bg=bg_color).grid(row=1, column=0, sticky="e")
        self.spin_extremas = tk.Spinbox(frame_config, from_=0, to=100, width=5)
        self.spin_extremas.delete(0, "end")
        self.spin_extremas.insert(0, 5)
        self.spin_extremas.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_config, text="Profundidad Base:", bg=bg_color).grid(row=1, column=2, sticky="e")
        self.spin_profundidad = tk.Spinbox(frame_config, from_=1, to=50, width=5)
        self.spin_profundidad.delete(0, "end")
        self.spin_profundidad.insert(0, 6)
        self.spin_profundidad.grid(row=1, column=3, padx=5, pady=5)

        # --- SECCIÓN 3: EJECUCIÓN ---
        frame_accion = tk.Frame(root, bg=bg_color, pady=10)
        frame_accion.pack(fill="x", padx=10)

        self.btn_generar = tk.Button(frame_accion, text="GENERAR CASOS Y EXPORTAR JSON", 
                                     command=self.ejecutar_generacion, 
                                     bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), height=2)
        self.btn_generar.pack(fill="x", padx=20)

        # --- SECCIÓN 4: RESULTADOS Y LOGS ---
        frame_log = tk.LabelFrame(root, text="Reporte de Métricas", padx=10, pady=10, bg=bg_color)
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_log = scrolledtext.ScrolledText(frame_log, height=15)
        self.txt_log.pack(fill="both", expand=True)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            self.ruta_gramatica.set(archivo)
            # Log visual
            self.log(f"Archivo seleccionado: {os.path.basename(archivo)}")

    def log(self, mensaje):
        self.txt_log.insert(tk.END, mensaje + "\n")
        self.txt_log.see(tk.END)

    def ejecutar_generacion(self):
        ruta = self.ruta_gramatica.get()
        if not ruta or ruta == "No seleccionado":
            messagebox.showwarning("Atención", "Por favor selecciona un archivo de gramática primero.")
            return

        try:
            # Obtener valores de la GUI
            n_val = int(self.spin_validas.get())
            n_inv = int(self.spin_invalidas.get())
            n_ext = int(self.spin_extremas.get())
            prof = int(self.spin_profundidad.get())

            self.log("-" * 40)
            self.log("🚀 Iniciando proceso de generación...")
            self.root.update() # Forzar actualización de UI

            # --- INVOCAR LA LÓGICA (BACKEND) ---
            generador = GeneradorCasos(ruta)
            gestor = GestorPruebas(generador)
            
            gestor.ejecutar_lote(n_validas=n_val, n_invalidas=n_inv, n_extremas=n_ext, config_profundidad=prof)
            
            # Exportar
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_json = f"resultado_pruebas_{timestamp}.json"
            gestor.exportar_json(nombre_json)

            # Mostrar Métricas en la GUI
            stats = gestor.estadisticas
            self.log("\n✅ PROCESO COMPLETADO")
            self.log(f"Total generado: {stats['total_generado']}")
            self.log(f"Tiempo: {stats['tiempo_total_ms']} ms")
            self.log(f"Longitud Promedio: {stats['longitud_promedio']}")
            self.log(f"Distribución: {stats['por_categoria']}")
            self.log(f"\nArchivo guardado en: {os.path.abspath(nombre_json)}")
            
            messagebox.showinfo("Éxito", f"Se han generado {stats['total_generado']} casos correctamente.")

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error: {str(e)}")
            self.log(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionGenerador(root)
    root.mainloop()