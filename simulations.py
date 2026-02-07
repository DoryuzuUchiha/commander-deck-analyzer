import random


def simulate_mulligans(
    cards,
    card_capabilities,
    color_identity,
    simulations=5000,
    max_mulligans=3
):
    results = {
        "simulations": simulations,
        "kept_hands": 0,
        "average_mulligans": 0,
        "hand_quality": {
            "excellent": 0,
            "keepable": 0,
            "bad": 0
        }
    }

    mulligan_counts = []

    deck = cards.copy()

    for _ in range(simulations):
        mulligans = 0

        while True:
            random.shuffle(deck)
            hand_size = 7 - mulligans
            hand = deck[:hand_size]

            quality = evaluate_hand(hand, card_capabilities, color_identity)

            if quality != "bad" or mulligans >= max_mulligans:
                results["hand_quality"][quality] += 1
                mulligan_counts.append(mulligans)
                results["kept_hands"] += 1
                break

            mulligans += 1

    results["average_mulligans"] = round(
        sum(mulligan_counts) / len(mulligan_counts), 2
    )

    for k in results["hand_quality"]:
        results["hand_quality"][k] = round(
            results["hand_quality"][k] / simulations, 2
        )

    results["keep_rate"] = round(
        1 - results["hand_quality"]["bad"], 2
    )

    return results


def evaluate_hand(hand, card_capabilities, color_identity):
    lands = 0
    ramp = 0
    colors_available = set()

    for card in hand:
        caps = card_capabilities.get(card, {})

        if "land" in caps.get("types", []):
            lands += 1

        if caps.get("mana"):
            ramp += 1
            for source in caps["mana"]:
                for color in source.get("produces", []):
                    colors_available.add(color)

    missing_colors = set(color_identity) - colors_available

    if lands < 2:
        return "bad"

    if lands >= 2 and ramp >= 1 and not missing_colors:
        return "excellent"

    return "keepable"
