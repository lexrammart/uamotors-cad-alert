"""
General application configuration.
Contains integration constants and regular expressions for monitoring.
"""
import re

WEBHOOK_URL = "https://discord.com/api/webhooks/1533621148678488064/3xr254C785OW7FaW_OEv45EOp-x4rAvusyFo1Cs4uxo1WIyNkS9ayz0yZbFGaneBoQZF"

# Target repository root directory to monitor
TARGET_FOLDER = "UAMOTORS"

# Base name used for notifications
BASE_NAME = "GENERAL ASSEMBLY"

# Regular expressions to identify assembly versions and temporary lock files
ASSEMBLY_PATTERN = r"^GENERAL ASSEMBLY v\d+\.SLDASM$"
LOCK_PATTERN = r"^~\$GENERAL ASSEMBLY v\d+\.SLDASM$"

# Local installation environment configuration
INSTALL_FOLDER_NAME = "UAMotorsCAD"
SOCKET_PORT = 47255
