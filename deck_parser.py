def parse_deck(input_data):
    """
    Accepts either:
    - a file path
    - raw decklist text
    Returns (cards, commander_name)
    """

    if "\n" in input_data:
        lines = input_data.splitlines()
    else:
        with open(input_data, "r", encoding="utf-8") as f:
            lines = f.readlines()

    cards = []
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

        for _ in range(qty):
            cards.append(name)

        # Assume last listed card is commander (EDH-style)
        commander = name

    return cards, commander
