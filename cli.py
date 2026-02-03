from deck import Deck
from capabilities import fetch_card_data, extract_capabilities
from deck_parser import parse_deck


def main():
    # Parse deck.txt
    parsed_cards, commander_name = parse_deck("deck.txt")
    deck = Deck(parsed_cards, commander_name)

    # ------------------------------
    # FETCH COMMANDER (MANDATORY)
    # ------------------------------
    commander_data = fetch_card_data(commander_name, commander_name)
    commander_caps = extract_capabilities(commander_data)

    deck.set_commander_capabilities(
        commander_caps,
        commander_caps.get("cmc")
    )

    # ------------------------------
    # FETCH ALL DECK CARDS
    # ------------------------------
    for card in deck.cards:
        card_data = fetch_card_data(card.name, commander_name)
        card_caps = extract_capabilities(card_data)
        deck.add_card_capabilities(card.name, card_caps)

    # ------------------------------
    # ANALYZE
    # ------------------------------
    deck.analyze()


if __name__ == "__main__":
    main()
