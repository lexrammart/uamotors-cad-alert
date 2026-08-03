import requests
import threading
import time
import queue
import config

_message_queue = queue.Queue()


def _discord_worker():
    while True:
        message = _message_queue.get()
        while True:
            try:
                response = requests.post(
                    config.WEBHOOK_URL, json={"content": message}, timeout=10
                )
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                break
            except Exception:
                # Network failure
                time.sleep(15)
        _message_queue.task_done()


_worker_thread = threading.Thread(target=_discord_worker, daemon=True)
_worker_thread.start()


def send_discord(message):
    # Just put the message in the queue and return instantly
    _message_queue.put(message)
