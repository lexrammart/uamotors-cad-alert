import os
import subprocess
from watchdog.events import FileSystemEventHandler

import config
from discord_utils import send_discord


def buscar_carpeta_uamotors():
    user_home = os.path.expanduser("~")
    for nombre in ["Google Drive", "Drive", "GoogleDrive"]:
        ruta = os.path.join(user_home, nombre, "UAMOTORS")
        if os.path.exists(ruta):
            return ruta

    letras = [f"{chr(i)}:\\" for i in range(ord("D"), ord("Z") + 1)]
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
        output = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq SLDWORKS.exe"', shell=True
        ).decode(errors="ignore")
        return "sldworks.exe" in output.lower()
    except Exception:
        return True


class SWMonitorHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.active_lock_paths = set()

    def on_created(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == config.LOCK_FILE_NAME.lower():
            self.active_lock_paths.add(event.src_path)
            send_discord(
                f"🔴**[OCUPADO]**: Ensamble en uso (`{config.NOMBRE_ENSAMBLE}`)"
            )

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if filename.lower() == config.LOCK_FILE_NAME.lower():
            if event.src_path in self.active_lock_paths:
                self.active_lock_paths.remove(event.src_path)
            send_discord(
                f"🟢**[LIBRE]**: Ensamble disponible (`{config.NOMBRE_ENSAMBLE}`)"
            )
