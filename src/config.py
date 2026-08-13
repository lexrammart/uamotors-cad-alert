"""
General application configuration.
Contains integration constants and regular expressions for monitoring.
"""

import re
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1533988281195171962/nv3cJEvWrUhcEPDo1zH5zjcABusHsdbl65PCaYNPJwpXtLg6gPWTp1DcxH7OOVyEI5nM"

# Target repository root directory to monitor
TARGET_FOLDER = "UAMOTORS"

# Base name used for notifications
BASE_NAME = "OP-01assembly"

# Regular expressions to identify assembly versions and temporary lock files
ASSEMBLY_PATTERN = r"^OP-01assembly\d+\.SLDASM$"
LOCK_PATTERN = r"^~\$OP-01assembly\d+\.SLDASM$"

# Local installation environment configuration
INSTALL_FOLDER_NAME = "UAMotorsCAD"
SOCKET_PORT = 47255

## --DEVELOPER MODE--
DEBUG = True
DEV_WEBHOOK_URL = "https://discord.com/api/webhooks/1537230363766689914/Jij7QPz07-IfrmHdgDhEB762T2BsguRg0_73hr1QakDtPCcObrof--Gbk3rDt5_WVjBy"

# test paths
MAC_DRIVE_UAMOTORS_PATH = "/Users/alejandro/Library/CloudStorage/GoogleDrive-al2242000248@azc.uam.mx/Shared drives/UAMOTORS"
MAC_TEST_SW_PATH = "/Users/alejandro/Library/CloudStorage/GoogleDrive-al2242000248@azc.uam.mx/Shared drives/UAMOTORS/2026/Design/Electronics/SW"
DEV_TARGET_FOLDER = "./test_env/UAMOTORS"

REL_DRIVE_DB_PATH = os.path.join(
    "2026",
    "Design",
    "Electronics",
    "Data-Code telemetry",
    "auamotors_cad_alert",
    "authorized_users.uamotors",
)


def get_appdata_dir():
    """Returns local storage path"""

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local"))
    else:
        base = os.path.expanduser("~/.config")

    path = os.path.join(base, INSTALL_FOLDER_NAME)
    os.makedirs(path, exist_ok=True)

    return path
