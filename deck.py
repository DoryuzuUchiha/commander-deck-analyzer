from otags import get_card_otags


class Card:
    def __init__(self, name, data):
        self.name = name
        self.type_line = data["type_line"]
        self.cmc = data.get("cmc", 0)
        self.colors = data.get("colors", [])
        self.oracle_text = data.get("oracle_text", "")

        self.is_land = "Land" in self.type_line
        self.is_basic = "Basic Land" in self.type_line

        # PRIMARY tagging source (community-curated)
        self.tags = get_card_otags(self.name)


class Deck:
    def __init__(self):
        self.cards = []  # list of (Card, qty)

    def add(self, card, qty):
        self.cards.append((card, qty))

    @property
    def library_size(self):
        return 99  # Commander rule

    @property
    def land_count(self):
        return sum(qty for card, qty in self.cards if card.is_land)

    @property
    def ramp_count(self):
        # Ramp now comes from otags
        return sum(qty for card, qty in self.cards if "ramp" in card.tags)

    def validate_singleton(self):
        seen = set()
        for card, qty in self.cards:
            if card.is_basic:
                continue
            if qty > 1:
                raise ValueError(f"Illegal duplicate: {card.name}")
            if card.name in seen:
                raise ValueError(f"Illegal duplicate: {card.name}")
            seen.add(card.name)
