import os
import json
from .config import CONFIG, logger

class QueueManager:
    def __init__(self, queue_file=None):
        self.queue_file = queue_file or CONFIG.get("queue_file", "queue.json")
        self.queue_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.queue_file)
        self.queue = self._load_queue()

    def _load_queue(self):
        if os.path.exists(self.queue_file_path):
            try:
                with open(self.queue_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing queue file {self.queue_file_path}. Starting with empty queue.")
                return []
        return []

    def _save_queue(self):
        with open(self.queue_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, indent=4)

    def add(self, item):
        """Fügt ein Item (z.B. ein Dateipfad-Dictionary) zur Queue hinzu, wenn es noch nicht existiert."""
        if item not in self.queue:
            self.queue.append(item)
            self._save_queue()
            logger.info(f"Added to queue: {item}")
        else:
            logger.debug(f"Item already in queue: {item}")

    def pop(self):
        """Holt das nächste Item aus der Queue und speichert den neuen Zustand."""
        if self.queue:
            item = self.queue.pop(0)
            self._save_queue()
            return item
        return None

    def get_all(self):
        return self.queue

    def is_empty(self):
        return len(self.queue) == 0
