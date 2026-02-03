"""
tags.py

Lightweight fallback tags when a card has no otags.
This should NEVER override otags.
"""

def fallback_tags(card):
    tags = set()

    if card.is_land:
        tags.add("land")

    if card.cmc <= 2:
        tags.add("early_game")

    return tags
