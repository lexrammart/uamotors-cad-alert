"""
SolidWorks and file system status monitoring.
Detects the creation and deletion of temporary lock files
to infer the usage status of assemblies.
"""

import os
import subprocess
import re
from watchdog.events import FileSystemEventHandler
import src.config as config
from src.services.discord_service import send_discord
from src.services.user_service import load_local_profile


def es_bloqueo_real_sw(filepath):
    """
    Attempts to open the lock file in append mode.
    If a PermissionError is raised, the local SolidWorks process holds an exclusive lock.
    If it succeeds, it's either a ghost file or a synced file from another user's Drive.
    """
    try:
        with open(filepath, 'a'):
            pass
        return False
    except PermissionError:
        return True
    except Exception:
        # En caso de otro error (ej. archivo ya no existe), asumimos que no está bloqueado 
        return False


def _verificar_ensamble(ruta):
    """
    Recursively verifies if a directory contains any file
    matching the expected assembly pattern.

    Args:
        ruta (str): Root directory to inspect.

    Returns:
        bool: True if a valid file is found, False otherwise.
    """
    for root, _, files in os.walk(ruta):
        for f in files:
            if re.match(config.ASSEMBLY_PATTERN, f, re.IGNORECASE):
                return True
    return False


def buscar_carpeta_uamotors():
    """
    Searches for the configured target path in local and cloud drives.
    Validates the found folder using _verificar_ensamble().

    Returns:
        str or None: The absolute path of the validated folder, or None if not found.
    """
    user_home = os.path.expanduser("~")
    for nombre in ["Google Drive", "Drive", "GoogleDrive"]:
        ruta = os.path.join(user_home, nombre, config.TARGET_FOLDER)
        if os.path.exists(ruta) and _verificar_ensamble(ruta):
            return ruta

    letras = [f"{chr(i)}:\\" for i in range(ord("D"), ord("Z") + 1)]
    for disco in letras:
        if os.path.exists(disco):
            try:
                for root, dirs, _ in os.walk(disco):
                    for d in dirs:
                        if d.upper() == config.TARGET_FOLDER.upper():
                            ruta_candidata = os.path.join(root, d)
                            if _verificar_ensamble(ruta_candidata):
                                return ruta_candidata
                    if root.count(os.sep) - disco.count(os.sep) >= 2:
                        dirs.clear()
            except Exception:
                continue
    return None


def sldworks_esta_abierto():
    """
    Verifies via command line if the SolidWorks process
    is currently active in the operating system's task list.

    Returns:
        bool: True if the process is running or if an error occurs, False otherwise.
    """
    try:
        output = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq SLDWORKS.exe"', shell=True
        ).decode(errors="ignore")
        return "sldworks.exe" in output.lower()
    except Exception:
        return True


class SWMonitorHandler(FileSystemEventHandler):
    """
    File system event handler.
    Reacts to file creation and deletion to update the assembly status.
    """

    def __init__(self):
        super().__init__()
        self.active_lock_paths = set()
        
        # Cargar perfil del usuario actual para las alertas
        profile = load_local_profile()
        if profile:
            self.user_display = f"{profile.get('nombre', 'Usuario')} ({profile.get('email', '')})"
        else:
            self.user_display = "Usuario Desconocido"

    def on_created(self, event):
        filename = os.path.basename(event.src_path)
        if re.match(config.LOCK_PATTERN, filename, re.IGNORECASE):
            # Solo notificar si el archivo está realmente bloqueado por el SO local
            if not es_bloqueo_real_sw(event.src_path):
                return
                
            self.active_lock_paths.add(event.src_path)
            real_name = filename[2:]
            send_discord(f"🔴 **[OCUPADO]:** Ensamble en uso (`{real_name}`) por **{self.user_display}**")

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if re.match(config.LOCK_PATTERN, filename, re.IGNORECASE):
            if event.src_path in self.active_lock_paths:
                self.active_lock_paths.remove(event.src_path)
                real_name = filename[2:]
                send_discord(f"🟢 **[LIBRE]:** Ensamble disponible (`{real_name}`) - Liberado por **{self.user_display}**")
