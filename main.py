import os
import time
import traceback
from watchdog.observers import Observer

import config
from discord_utils import send_discord
from installer import check_single_instance, auto_instalar
from monitor import buscar_carpeta_uamotors, sldworks_esta_abierto, SWMonitorHandler

if __name__ == "__main__":
    try:
        check_single_instance()
        auto_instalar()

        ruta_activa = buscar_carpeta_uamotors()
        if ruta_activa:
            send_discord(f"⚙️ Monitoreo de CAD activo para: `{config.NOMBRE_ENSAMBLE}`")
            event_handler = SWMonitorHandler()
            observer = Observer()
            observer.schedule(event_handler, path=ruta_activa, recursive=True)
            observer.start()

            try:
                while True:
                    time.sleep(5)
                    # para cuando sw crashee o se cierre desde el task manager
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
