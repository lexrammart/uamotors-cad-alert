"""
Main entry point for the UAMOTORS CAD alert monitor.
Coordinates instance verification, automatic installation, and the startup
of the file system event monitor.
"""

import os
import time
import traceback
from watchdog.observers import Observer

import src.config as config
from src.services.discord_service import send_discord
from src.installer.installer import (
    check_single_instance,
    auto_instalar,
    verificar_registro_usuario,
)
from src.core.monitor import (
    buscar_carpeta_uamotors,
    sldworks_esta_abierto,
    SWMonitorHandler,
)

if __name__ == "__main__":
    try:
        check_single_instance()
        auto_instalar()

        ruta_activa = buscar_carpeta_uamotors()
        if ruta_activa:
            import sys
            if not verificar_registro_usuario(ruta_activa):
                sys.exit()

            send_discord(
                f"⚙️ Monitoreo de CAD activo desde un nuevo equipo para: `{config.BASE_NAME}`"
            )
            event_handler = SWMonitorHandler()
            observer = Observer()
            observer.schedule(event_handler, path=ruta_activa, recursive=True)
            observer.start()

            try:
                while True:
                    time.sleep(5)
                    # crash de sw o cierre desde task manager
                    if not sldworks_esta_abierto():
                        for lock_path in list(event_handler.active_lock_paths):
                            if os.path.exists(lock_path):
                                try:
                                    os.remove(lock_path)
                                except Exception:
                                    pass
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        else:
            pass
    except Exception as e:
        error_path = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local")),
            "UAMotorsCAD_error.txt",
        )
        with open(error_path, "w") as f:
            f.write(traceback.format_exc())
