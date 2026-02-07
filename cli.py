from deck_parser import parse_deck
from capabilities import fetch_card_data, extract_capabilities
from deck import Deck
import json
import os

DECK_PATH = "deck.txt"
CACHE_PATH = "cache/analysis.json"


def main():
    # Parse deck.txt
    cards, commander_name = parse_deck(DECK_PATH)

    # Fetch commander data
    commander_data = fetch_card_data(commander_name)

    # Initialize deck
    deck = Deck(cards, commander_data)

    # Fetch and analyze each card
    for card_name in cards:
        card_data = fetch_card_data(card_name)
        caps = extract_capabilities(card_data)
        deck.add_card_capabilities(card_name, caps)

    # Run analysis
    analysis = deck.analyze()

    # Ensure cache directory exists
    os.makedirs("cache", exist_ok=True)

    # Save analysis
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    print("Analysis complete.")


if __name__ == "__main__":
    main()
