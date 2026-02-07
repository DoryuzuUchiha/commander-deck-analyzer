import os
import json
import requests
from itertools import islice

SCRYFALL_COLLECTION_API = "https://api.scryfall.com/cards/collection"
CACHE_DIR = "cache/scryfall"
MAX_BATCH = 75


def _cache_path(name: str) -> str:
    safe = name.replace("/", "_").strip()
    return os.path.join(CACHE_DIR, f"{safe}.json")


def _chunks(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk


def fetch_cards_bulk(names: list[str]) -> dict:
    """
    Fetch multiple cards using Scryfall's collection endpoint.
    Safe for Commander decks (handles >75 cards and bad names).
    Returns { lowercase_name: card_json }
    """

    os.makedirs(CACHE_DIR, exist_ok=True)

    results = {}
    missing = []

    # 1️⃣ Load cached cards
    for name in names:
        clean = name.strip()
        path = _cache_path(clean)

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                results[clean.lower()] = json.load(f)
        else:
            missing.append(clean)

    if not missing:
        return results

    # 2️⃣ Fetch missing cards in safe batches
    for batch in _chunks(missing, MAX_BATCH):
        payload = {
            "identifiers": [{"name": n} for n in batch]
        }

        response = requests.post(
            SCRYFALL_COLLECTION_API,
            json=payload,
            timeout=15
        )

        # Handle bad batch gracefully
        if response.status_code != 200:
            print("⚠️ Scryfall batch failed:")
            print(response.text)
            continue

        data = response.json().get("data", [])

        for card in data:
            name = card["name"]
            path = _cache_path(name)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(card, f, indent=2)

            results[name.lower()] = card

    return results
