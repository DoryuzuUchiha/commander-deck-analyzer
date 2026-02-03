import requests
import json
import os

CACHE_DIR = "cache"

def _cache_path(name):
    safe = name.lower().replace(" ", "_").replace(",", "")
    return os.path.join(CACHE_DIR, f"{safe}.json")

def get_card(name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _cache_path(name)

    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    url = "https://api.scryfall.com/cards/named"
    r = requests.get(url, params={"exact": name})
    r.raise_for_status()
    card = r.json()

    with open(path, "w") as f:
        json.dump(card, f, indent=2)

    return card
