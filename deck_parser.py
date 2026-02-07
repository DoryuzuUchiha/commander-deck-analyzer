def parse_deck(input_data):
    """
    Accepts either:
    - a file path
    - raw decklist text

    Returns:
    - flat_cards: list[str]     (expanded by quantity)
    - unique_cards: list[str]   (unique names, for bulk fetch)
    - commander_name: str
    """

    if "\n" in input_data:
        lines = input_data.splitlines()
    else:
        with open(input_data, "r", encoding="utf-8") as f:
            lines = f.readlines()

    flat_cards = []
    unique_cards = []
    commander = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            qty, name = line.split(" ", 1)
            qty = int(qty)
        except ValueError:
            continue

        # Track unique cards once (for Scryfall batch fetch)
        if name not in unique_cards:
            unique_cards.append(name)

        # Expand quantities for gameplay logic
        for _ in range(qty):
            flat_cards.append(name)

        # Assume last listed card is commander (EDH-style)
        commander = name

    return flat_cards, unique_cards, commander
