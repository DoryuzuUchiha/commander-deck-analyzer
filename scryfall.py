import os
import json
import time
import requests

SCRYFALL_API = "https://api.scryfall.com/cards/named"
CACHE_DIR = "cache/scryfall"

def fetch_card(name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{name}.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    response = requests.get(SCRYFALL_API, params={"exact": name})
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch card: {name}")

    data = response.json()

    if "oracle_id" not in data:
        raise RuntimeError(f"No oracle_id for card: {name}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    time.sleep(0.1)
    return data
