import requests
import config

def send_discord(message):
    try:
        requests.post(config.WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception:
        pass
