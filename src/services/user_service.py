"""
User authorization whitelist and local profile service.
"""

import os
import json
import base64
import src.config as config


def get_profile_file_path():
    """Returns absolute path to local profile (.uamotors)."""
    return os.path.join(config.get_appdata_dir(), "user_profile.uamotors")


def load_local_profile():
    """Reads and decodes user_profile.uamotors if it exists, otherwise returns None."""
    profile_path = get_profile_file_path()

    if os.path.exists(profile_path):
        try:
            with open(profile_path, "rb") as f:
                encoded_bytes = f.read()
            json_str = base64.b64decode(encoded_bytes).decode("utf-8")
            return json.loads(json_str)
        except Exception:
            return None

    return None


def save_local_profile(email, name):
    """Saves verified user profile encoded in base64 inside user_profile.uamotors."""
    profile_path = get_profile_file_path()

    data = {
        "email": email.strip().lower(),
        "name": name.strip(),
    }

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    encoded_bytes = base64.b64encode(json_str.encode("utf-8"))

    with open(profile_path, "wb") as f:
        f.write(encoded_bytes)

    return data


def load_drive_whitelist(ruta_uamotors):
    """Reads and decodes authorized_users.uamotors from Google Drive."""
    db_path = os.path.join(ruta_uamotors, config.REL_DRIVE_DB_PATH)

    if not os.path.exists(db_path):
        return None

    try:
        with open(db_path, "rb") as f:
            encoded_bytes = f.read()
        json_str = base64.b64decode(encoded_bytes).decode("utf-8")
        return json.loads(json_str)
    except Exception:
        return None


def verify_user_email(email, ruta_uamotors):
    """
    Verifies if an email is valid and registered in the Drive whitelist.
    
    Returns:
        tuple: (bool success, str name_or_none, str error_msg)
    """
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, None, "Por favor ingresa un correo electrónico válido."

    whitelist = load_drive_whitelist(ruta_uamotors)
    if whitelist is None:
        return (
            False,
            None,
            f"No se encontró la BD de usuarios en Drive ({config.REL_DRIVE_DB_PATH}).",
        )

    if email_clean in whitelist:
        user_info = whitelist[email_clean]
        name = user_info.get("nombre", "Usuario Autorizado")
        return True, name, ""
    else:
        return (
            False,
            None,
            "El correo no está registrado en la lista de usuarios autorizados de UAMOTORS.",
        )

