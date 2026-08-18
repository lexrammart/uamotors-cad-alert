import sys
import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet

def get_encryption_key():
    secret = "UAMOTORS_2026_CAD_ELECTRONICS"
    salt = "UAMOTORS_CAD_ALERT_SALT"
    key = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
    return base64.urlsafe_b64encode(key)

path = "/Users/alejandro/Library/CloudStorage/GoogleDrive-al2242000248@azc.uam.mx/Shared drives/UAMOTORS/2026/Design/Electronics/CAD-Alert/authorized_users.uamotors"

try:
    with open(path, "rb") as f:
        encrypted_data = f.read()
    fernet = Fernet(get_encryption_key())
    decrypted_data = fernet.decrypt(encrypted_data).decode("utf-8")
    loaded_json = json.loads(decrypted_data)
    print(json.dumps(loaded_json, indent=2))
except Exception as e:
    print("Error:", e)
