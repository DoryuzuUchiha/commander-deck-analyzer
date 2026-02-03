import sys

from deck_parser import parse_deck
from scryfall import get_card
from deck import Card, Deck
from analysis import land_consistency, ramp_consistency
from tag_stats import generate_tag_statistics


def main():
    if len(sys.argv) != 2:
        print("Usage: python cli.py deck.txt")
        sys.exit(1)

    deck_path = sys.argv[1]

    # -----------------------------
    # Build the deck
    # -----------------------------
    decklist = parse_deck(deck_path)
    deck = Deck()

    print("Loading deck and fetching Scryfall data...\n")

    for qty, name in decklist:
        data = get_card(name)
        card = Card(name, data)
        deck.add(card, qty)

    # -----------------------------
    # Commander validation
    # -----------------------------
    try:
        deck.validate_singleton()
    except ValueError as e:
        print(f"Deck validation error: {e}")
        sys.exit(1)

    # -----------------------------
    # Basic deck info
    # -----------------------------
    print("\nCommander Deck Analysis")
    print("=" * 40)
    print(f"Library size: {deck.library_size}")
    print(f"Lands: {deck.land_count}")
    print(f"Ramp sources: {deck.ramp_count}")

    # -----------------------------
    # Hypergeometric stats
    # -----------------------------
    print("\nLand Consistency (Hypergeometric)")
    print("-" * 40)
    land_stats = land_consistency(deck)
    for label, value in land_stats.items():
        print(f"{label}: {value:.2%}")

    print("\nRamp Consistency (Hypergeometric)")
    print("-" * 40)
    ramp_stats = ramp_consistency(deck)
    for label, value in ramp_stats.items():
        print(f"{label}: {value:.2%}")

    # -----------------------------
    # Tag-based stats (big dump)
    # -----------------------------
    print("\nTag-Based Deck Statistics")
    print("=" * 40)

    tag_stats = generate_tag_statistics(deck)

    for key, value in tag_stats.items():
        print(f"{key}: {value}")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
