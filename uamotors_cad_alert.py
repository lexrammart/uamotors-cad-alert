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

WEBHOOK_URL = "https://discord.com/api/webhooks/1533631167461331026/Aj_RamYRz4-nv8I4DkS6lQjm7yjlyncQpJLlnaqWz7ys9qiKJZgIUZckhB1mgv4Z3tMk"
NOMBRE_ENSAMBLE = "GENERAL ASSEMBLY E.SLDASM"
LOCK_FILE_NAME = f"~${NOMBRE_ENSAMBLE}"
USUARIO = f"{os.getlogin()} ({platform.node()})"

def buscar_carpeta_uamotors():
    # 1. Buscar en la carpeta personal del usuario
    user_home = os.path.expanduser("~")
    for nombre in ["Google Drive", "Drive", "GoogleDrive"]:
        ruta = os.path.join(user_home, nombre, "UAMOTORS")
        if os.path.exists(ruta):
            return ruta

    # 2. Escaneo dinámico de discos (G:, H:, I:, etc.) sin importar si está en inglés o español
    letras = [f"{chr(i)}:\\" for i in range(ord('D'), ord('Z') + 1)]
    for disco in letras:
        if os.path.exists(disco):
            try:
                # Revisa la raíz y subcarpetas inmediatas (My Drive, Mi unidad, Unidades compartidas, Shared drives)
                for root, dirs, _ in os.walk(disco):
                    for d in dirs:
                        if d.upper() == "UAMOTORS":
                            return os.path.join(root, d)
                    # Limita la búsqueda a 2 niveles de profundidad para no ralentizar el inicio
                    if root.count(os.sep) - disco.count(os.sep) >= 2:
                        dirs.clear()
            except Exception:
                continue
    return None

def send_discord(message):
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception:
        pass

def auto_instalar():
    startup_folder = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
    actual_path = sys.executable
    target_path = os.path.join(startup_folder, os.path.basename(actual_path))

    if os.path.dirname(actual_path).lower() != startup_folder.lower():
        try:
            shutil.copy2(actual_path, target_path)
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("UAMOTORS CAD", "¡Instalación completada!\nLas alertas de SolidWorks quedaron activadas.")
            os.startfile(target_path)
            sys.exit()
        except Exception:
            pass

class SWMonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == LOCK_FILE_NAME.lower():
            send_discord(f"🔴 **{USUARIO}** abrió el ensamble (`{NOMBRE_ENSAMBLE}`). **[OCUPADO]**")

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == LOCK_FILE_NAME.lower():
            send_discord(f"🟢 **{USUARIO}** cerró el ensamble (`{NOMBRE_ENSAMBLE}`). **[LIBRE]**")

if __name__ == "__main__":
    auto_instalar()
    
    ruta_activa = buscar_carpeta_uamotors()
    if ruta_activa:
        send_discord(f"⚙️ **{USUARIO}** activo y monitoreando en: `{ruta_activa}`")
        event_handler = SWMonitorHandler()
        observer = Observer()
        observer.schedule(event_handler, path=ruta_activa, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        send_discord(f"⚠️ **{USUARIO}**: No se encontró la carpeta UAMOTORS en ningún disco.")
