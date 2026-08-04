"""
Discord integration module.
Implements a background queue to guarantee notification delivery
regardless of temporary network failures.
"""
import requests
import threading
import time
import queue
import config

_message_queue = queue.Queue()

def _discord_worker():
    """
    Background process that pulls messages from the queue and sends them to Discord.
    Implements retries in case of rate limits (429) or connection failures.
    """
    while True:
        message = _message_queue.get()
        while True:
            try:
                response = requests.post(config.WEBHOOK_URL, json={"content": message}, timeout=10)
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                break
            except Exception:
                time.sleep(15)
        _message_queue.task_done()

_worker_thread = threading.Thread(target=_discord_worker, daemon=True)
_worker_thread.start()

def send_discord(message):
    """
    Adds a message to the Discord send queue without blocking execution.
    
    Args:
        message (str): The content of the message to send.
    """
    _message_queue.put(message)
