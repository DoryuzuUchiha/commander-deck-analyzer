"""
otags.py

Fetches and caches Scryfall Oracle Tags (otags) and maps them
to internal Commander-relevant tags.
"""

import json
import os
import requests
from collections import defaultdict

OTAG_CACHE_PATH = os.path.join("cache", "otags.json")

SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards/search"

# -------------------------------------------------
# Which otags we care about (Commander-focused)
# -------------------------------------------------
OTAGS_OF_INTEREST = [
    "ramp",
    "mana-rock",
    "draw",
    "card-advantage",
    "tutor",
    "removal",
    "wipe",
    "counterspell",
    "recursion",
    "token-generator",
]

# -------------------------------------------------
# Normalize Scryfall otags → internal tags
# -------------------------------------------------
OTAG_NORMALIZATION = {
    "ramp": "ramp",
    "mana-rock": "ramp",
    "draw": "card_draw",
    "card-advantage": "card_advantage",
    "tutor": "tutor",
    "removal": "single_target_removal",
    "wipe": "board_wipe",
    "counterspell": "counterspell",
    "recursion": "recursion",
    "token-generator": "token_generator",
}


# -------------------------------------------------
# Public API
# -------------------------------------------------
def load_otag_cache():
    if os.path.exists(OTAG_CACHE_PATH):
        with open(OTAG_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_otag_cache(cache):
    os.makedirs(os.path.dirname(OTAG_CACHE_PATH), exist_ok=True)
    with open(OTAG_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def get_card_otags(card_name):
    """
    Returns a set of normalized internal tags for a card name
    using cached Scryfall otags.
    """
    cache = load_otag_cache()
    return set(cache.get(card_name, []))


# -------------------------------------------------
# Cache builder (run manually or once on startup)
# -------------------------------------------------
def build_otag_cache(force_refresh=False):
    if os.path.exists(OTAG_CACHE_PATH) and not force_refresh:
        print("Otag cache already exists. Skipping rebuild.")
        return

    print("Building otag cache from Scryfall...")
    card_to_tags = defaultdict(set)

    for otag in OTAGS_OF_INTEREST:
        print(f"Fetching otag:{otag}")

        url = SCRYFALL_SEARCH_URL
        params = {"q": f"otag:{otag}"}

        try:
            while True:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                for card in data["data"]:
                    name = card["name"]
                    internal_tag = OTAG_NORMALIZATION.get(otag)
                    if internal_tag:
                        card_to_tags[name].add(internal_tag)

                if data.get("has_more"):
                    url = data["next_page"]
                    params = None
                else:
                    break

        except requests.exceptions.HTTPError as e:
            print(f"⚠️  Skipping invalid otag: {otag}")
            continue

    cache = {name: sorted(tags) for name, tags in card_to_tags.items()}
    save_otag_cache(cache)

    print(f"Otag cache built with {len(cache)} cards.")

