import json
import os

CACHE_PATH = "cache/capabilities.json"

class CapabilityCache:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get(self, oracle_id):
        return self.data.get(oracle_id)

    def set(self, oracle_id, caps):
        self.data[oracle_id] = caps

    def save(self):
        os.makedirs("cache", exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
