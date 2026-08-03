import os
import sys
import shutil
import time
import subprocess
import requests
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WEBHOOK_URL = "https://discord.com/api/webhooks/1533631167461331026/Aj_RamYRz4-nv8I4DkS6lQjm7yjlyncQpJLlnaqWz7ys9qiKJZgIUZckhB1mgv4Z3tMk"
NOMBRE_ENSAMBLE = "GENERAL ASSEMBLY E.SLDASM"
LOCK_FILE_NAME = f"~${NOMBRE_ENSAMBLE}"

def buscar_carpeta_uamotors():
    user_home = os.path.expanduser("~")
    for nombre in ["Google Drive", "Drive", "GoogleDrive"]:
        ruta = os.path.join(user_home, nombre, "UAMOTORS")
        if os.path.exists(ruta):
            return ruta

    letras = [f"{chr(i)}:\\" for i in range(ord('D'), ord('Z') + 1)]
    for disco in letras:
        if os.path.exists(disco):
            try:
                for root, dirs, _ in os.walk(disco):
                    for d in dirs:
                        if d.upper() == "UAMOTORS":
                            return os.path.join(root, d)
                    if root.count(os.sep) - disco.count(os.sep) >= 2:
                        dirs.clear()
            except Exception:
                continue
    return None

def sldworks_esta_abierto():
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq SLDWORKS.exe"', shell=True).decode(errors='ignore')
        return "SLDWORKS.exe" in output
    except Exception:
        return True

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
            send_discord(f"🔴 **Ensamble en uso** (`{NOMBRE_ENSAMBLE}`) **[OCUPADO]**")

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == LOCK_FILE_NAME.lower():
            send_discord(f"🟢 **Ensamble disponible** (`{NOMBRE_ENSAMBLE}`) **[LIBRE]**")

if __name__ == "__main__":
    auto_instalar()
    
    ruta_activa = buscar_carpeta_uamotors()
    if ruta_activa:
        send_discord(f"⚙️ Monitoreo de CAD activo para: `{NOMBRE_ENSAMBLE}`")
        event_handler = SWMonitorHandler()
        observer = Observer()
        observer.schedule(event_handler, path=ruta_activa, recursive=True)
        observer.start()
        
        lock_path_completo = os.path.join(ruta_activa, LOCK_FILE_NAME)
        
        try:
            while True:
                time.sleep(5)
                # Si existe el candado pero SolidWorks ya no está en ejecución, se elimina el candado huérfano
                if os.path.exists(lock_path_completo) and not sldworks_esta_abierto():
                    try:
                        os.remove(lock_path_completo)
                    except Exception:
                        pass
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        send_discord(f"⚠️ No se encontró la carpeta UAMOTORS para monitorear.")
