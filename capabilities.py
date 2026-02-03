import os
import json
import requests

SCRYFALL_API = "https://api.scryfall.com/cards/named"


def get_deck_cache_dir(commander_name):
    safe = commander_name.replace(" ", "_")
    path = os.path.join("cache", "decks", safe)
    os.makedirs(path, exist_ok=True)
    return path


def fetch_card_data(card_name, commander_name, use_cache=True):
    cache_dir = get_deck_cache_dir(commander_name)
    path = os.path.join(cache_dir, f"{card_name}.json")

    if use_cache and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    response = requests.get(SCRYFALL_API, params={"exact": card_name})
    response.raise_for_status()
    data = response.json()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def extract_capabilities(card_data):
    caps = {
        "types": [],
        "mana": [],
        "draw": [],
        "cmc": card_data.get("cmc"),
        "color_identity": card_data.get("color_identity", [])
    }

    type_line = card_data.get("type_line", "").lower()
    caps["types"] = type_line.split()

    # Mana production (ONLY repeatable if permanent)
    produced = card_data.get("produced_mana", [])
    if produced and ("artifact" in caps["types"] or "creature" in caps["types"] or "land" in caps["types"]):
        caps["mana"].append({
            "produces": produced,
            "repeatable": True,
            "source": "land" if "land" in caps["types"] else "nonland",
            "enters_tapped": False
        })

    return caps
