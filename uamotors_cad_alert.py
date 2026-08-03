import os
import sys
import shutil
import time
import platform
import requests
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================= CONFIGURACIÓN =================
WEBHOOK_URL = "https://discord.com/api/webhooks/1533631167461331026/Aj_RamYRz4-nv8I4DkS6lQjm7yjlyncQpJLlnaqWz7ys9qiKJZgIUZckhB1mgv4Z3tMk"
CARPETA_DRIVE = os.path.expanduser(r"~\Google Drive\UAMOTORS") # Ruta a la carpeta
NOMBRE_ENSAMBLE = "GENERAL ASSEMBLY E.SLDASM"
LOCK_FILE_NAME = f"~${NOMBRE_ENSAMBLE}"
USUARIO = f"{os.getlogin()} ({platform.node()})"
# =================================================

def auto_instalar():
    # Detecta la ruta de Inicio de Windows del usuario actual
    startup_folder = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
    actual_path = sys.executable
    target_path = os.path.join(startup_folder, os.path.basename(actual_path))

    # Si NO se está ejecutando desde la carpeta Startup, se auto-copia
    if os.path.dirname(actual_path).lower() != startup_folder.lower():
        try:
            shutil.copy2(actual_path, target_path)
            
            # Muestra aviso visual simple al usuario
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("UAMOTORS CAD", "¡Instalación completada!\nLas alertas de SolidWorks quedaron activadas.")
            
            # Ejecuta la versión copiada en Startup y cierra el instalador
            os.startfile(target_path)
            sys.exit()
        except Exception as e:
            pass # Si ocurre algún error de permiso, continúa la ejecución normal

class SWMonitorHandler(FileSystemEventHandler):
    def send_discord(self, message):
        try:
            requests.post(WEBHOOK_URL, json={"content": message})
        except Exception as e:
            pass

    def on_created(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == LOCK_FILE_NAME.lower():
            self.send_discord(f"🔴 **{USUARIO}** abrió el ensamble (`{NOMBRE_ENSAMBLE}`). **[OCUPADO]**")

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == LOCK_FILE_NAME.lower():
            self.send_discord(f"🟢 **{USUARIO}** cerró el ensamble (`{NOMBRE_ENSAMBLE}`). **[LIBRE]**")

if __name__ == "__main__":
    auto_instalar() # Se ejecuta antes de iniciar la vigilancia
    
    event_handler = SWMonitorHandler()
    observer = Observer()
    
    if os.path.exists(CARPETA_DRIVE):
        observer.schedule(event_handler, path=CARPETA_DRIVE, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()