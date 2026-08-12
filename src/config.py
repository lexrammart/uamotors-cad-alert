"""
General application configuration.
Contains integration constants and regular expressions for monitoring.
"""

import re

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
