"""
Application installation and instance control management.
Ensures the script runs uniquely and automates local user deployment.
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import socket

import src.config as config
from src.services.user_service import load_local_profile
from src.installer.gui import mostrar_ventana_registro

_instance_socket = None


def check_single_instance():
    """
    Ensures only a single instance of the application runs at a time
    by binding a local socket. Exits the application if the port is already in use.
    """
    global _instance_socket
    try:
        _instance_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _instance_socket.bind(("127.0.0.1", config.SOCKET_PORT))
    except socket.error:
        sys.exit()


def kill_previous_instance(executable_name):
    """
    Attempts to forcefully close any running instances of the application
    using taskkill on Windows.
    """
    if os.name == 'nt':
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", executable_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=0x08000000
            )
        except Exception:
            pass


def verificar_registro_usuario(ruta_uamotors):
    """
    Verifies if a local profile exists. If not, launches the GUI registration.
    Returns True if user is registered, False otherwise.
    """
    profile = load_local_profile()
    if profile:
        return True
    
    # User not registered, prompt GUI
    return mostrar_ventana_registro(ruta_uamotors)


def auto_instalar():
    """
    Manages the automatic installation of the application in the user's AppData directory.
    Checks for previous instances, creates necessary folders, copies the executable, and
    creates a shortcut in the Startup folder.
    """
    if config.DEBUG or os.name != "nt":
        print("Modo dev o no-Windows: Saltando auto-instalación.")
        return

    local_appdata = os.environ.get(
        "LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local")
    )
    install_folder = os.path.join(local_appdata, config.INSTALL_FOLDER_NAME)
    startup_folder = os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    actual_path = sys.executable
    executable_name = os.path.basename(actual_path)
    target_path = os.path.join(install_folder, executable_name)
    shortcut_path = os.path.join(
        startup_folder, os.path.splitext(executable_name)[0] + ".lnk"
    )
    legacy_exe_path = os.path.join(startup_folder, executable_name)

    if os.path.dirname(actual_path).lower() != install_folder.lower():
        kill_previous_instance(executable_name)
        if os.path.exists(legacy_exe_path):
            try:
                os.remove(legacy_exe_path)
            except PermissionError:
                root = tk.Tk()
                root.withdraw()
                messagebox.showwarning(
                    "Aplicación en Ejecución",
                    "La versión anterior se encuentra en ejecución en segundo plano.\n\n"
                    "Cierra la aplicación desde el Administrador de Tareas para actualizarla.",
                )
                sys.exit()
            except Exception:
                pass

        if not os.path.exists(install_folder):
            try:
                os.makedirs(install_folder)
            except Exception as e:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Error", f"No se pudo crear la carpeta de instalación.\n{e}"
                )
                sys.exit()

        try:
            shutil.copy2(actual_path, target_path)

            # acceso directo en startup
            ps_cmd = f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');$s.TargetPath='{target_path}';$s.Save()"
            kwargs = {}
            if os.name == "nt":
                kwargs["creationflags"] = 0x08000000
            subprocess.call(["powershell", "-Command", ps_cmd], **kwargs)

            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "UAMOTORS CAD",
                "¡Instalación completada!\nLas alertas de SolidWorks quedaron activadas.",
            )
            # cambia el directorio de trabajo para liberar la carpeta con el empaquetado
            os.chdir(install_folder)
            os.startfile(target_path)
            sys.exit()
        except PermissionError:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "Aplicación en Ejecución",
                "La aplicación ya se encuentra en ejecución en segundo plano.\n\n"
                "Cierra la versión actual desde el Administrador de Tareas para poder actualizarla.",
            )
            sys.exit()
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error de Instalación", f"Ocurrió un error inesperado al instalar:\n{e}"
            )
            sys.exit()
