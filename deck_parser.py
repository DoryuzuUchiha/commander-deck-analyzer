def parse_deck(path):
    """
    Parses a Commander decklist.

    Format:
      <main deck>
      (blank line)
      <commander>

    Example:
      1 Sol Ring
      17 Island
      12 Mountain

      1 Vivi Ornitier
    """

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    # Split on first blank line
    if "" not in lines:
        raise ValueError(
            "Decklist must contain a blank line separating the commander."
        )

    split_index = lines.index("")
    main_lines = lines[:split_index]
    commander_lines = lines[split_index + 1 :]

    if not commander_lines:
        raise ValueError("Commander section is empty.")

    # Parse main deck
    main_cards = []
    for line in main_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        count, name = line.split(" ", 1)
        main_cards.append((int(count), name.strip()))

    # Parse commander
    commander_cards = []
    for line in commander_lines:
        line = line.strip()
        if not line:
            continue

        count, name = line.split(" ", 1)
        commander_cards.append((int(count), name.strip()))

    if len(commander_cards) != 1:
        raise ValueError(
            "Commander section must contain exactly one card."
        )

    commander_count, commander_name = commander_cards[0]
    if commander_count != 1:
        raise ValueError("Commander count must be exactly 1.")

    return main_cards, commander_name
