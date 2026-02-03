def parse_deck(path):
    """
    Parses a decklist of the form:
    1 Sol Ring
    1 Arcane Signet
    37 Forest
    """
    deck = []

    with open(path) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            qty, *name = line.split()
            deck.append((int(qty), " ".join(name)))

    return deck
