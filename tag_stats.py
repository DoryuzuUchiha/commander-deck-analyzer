from collections import Counter


def generate_tag_statistics(deck):
    """
    Generates tag-based statistics from the deck.
    """

    tag_counts = Counter()

    for card, qty in deck.cards:
        for tag in card.tags:
            tag_counts[tag] += qty

    stats = {}

    stats["tag_counts"] = dict(tag_counts)

    # Existing derived stats (unchanged)
    stats["lands"] = tag_counts.get("land", 0)
    stats["total_ramp"] = tag_counts.get("ramp", 0)
    stats["card_draw"] = tag_counts.get("card_draw", 0)
    stats["tutors"] = tag_counts.get("tutor", 0)
    stats["interaction"] = (
        tag_counts.get("single_target_removal", 0)
        + tag_counts.get("board_wipe", 0)
        + tag_counts.get("counterspell", 0)
    )

    return stats
