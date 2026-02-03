def summarize_functions(deck):
    summary = {
        "ramp": 0,
        "draw": 0,
        "removal": 0
    }

    for card in deck.cards:
        caps = deck.capabilities.get(card.name, {})

        if caps.get("mana"):
            summary["ramp"] += card.count

        if caps.get("draw"):
            summary["draw"] += card.count

        if caps.get("removal"):
            summary["removal"] += card.count

    return summary
