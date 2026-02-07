from collections import Counter, defaultdict
from hypergeom import at_least, at_least_one
from capabilities import fetch_card_data


class DeckProfile:
    def __init__(self, deck, analysis):
        self.deck = deck
        self.analysis = analysis

    def build(self):
        consistency = self.consistency_profile()

        return {
            "identity": self.identity(),
            "color_demand": self.color_demand(),
            "mana_supply": self.mana_supply(),
            "castability": self.castability_snapshot(),

            "consistency": consistency,

            # ✅ template-compatible alias
            "variance": {
                "expected_lands_turn_4": consistency["expected_lands_turn_4"],
                "screw_risk": consistency["mana_screw_risk"],
                "flood_risk": consistency["mana_stall_risk"],
            },

            "summary": self.summary()
        }


    # ======================
    # Identity
    # ======================

    def identity(self):
        deck_size = len(self.deck.cards)
        land_count = self.analysis["counts"]["lands"]
        spell_count = deck_size - land_count

        total_cmc = 0
        counted_spells = 0

        for name in self.deck.cards:
            card = fetch_card_data(name)
            if not card.get("type_line", "").lower().startswith("land"):
                cmc = card.get("cmc")
                if cmc is not None:
                    total_cmc += cmc
                    counted_spells += 1

        avg_cmc = round(total_cmc / counted_spells, 2) if counted_spells else 0

        return {
            "deck_size": deck_size,
            "land_count": land_count,
            "spell_count": spell_count,
            "colors": self.analysis["commander"]["color_identity"],
            "avg_mana_value": avg_cmc,
            "note": "Average mana value is calculated from nonland cards only."
        }

    # ======================
    # Color Demand
    # ======================

    def color_demand(self):
        pip_counts = Counter()

        for name in self.deck.cards:
            card = fetch_card_data(name)
            mana_cost = card.get("mana_cost", "")
            for c in mana_cost:
                if c in "WUBRG":
                    pip_counts[c] += 1

        return {
            # ✅ template compatibility
            "raw_pips": dict(pip_counts),

            # ✅ clearer semantic name (for future use)
            "pips": dict(pip_counts),

            # ✅ human explanation
            "note": (
                "This shows how many colored mana symbols appear in your spells. "
                "Higher values mean greater reliance on that color."
            )
        }

    # ======================
    # Mana Supply
    # ======================

    def mana_supply(self):
        producing_lands = Counter()
        effective_sources = Counter()
        multicolor_lands = 0

        for name in self.deck.cards:
            card = fetch_card_data(name)
            if not card.get("type_line", "").lower().startswith("land"):
                continue

            produced = [c for c in card.get("produced_mana", []) if c in "WUBRG"]
            if not produced:
                continue

            if len(produced) > 1:
                multicolor_lands += 1

            for c in produced:
                producing_lands[c] += 1
                effective_sources[c] += 1 / len(produced)

        # ✅ BACKWARD-COMPATIBLE RETURN SHAPE
        return {
            # what the template already expects
            "fractional_sources": {
                c: round(v, 2) for c, v in effective_sources.items()
            },

            # clearer semantic names (future-proof)
            "effective_sources": {
                c: round(v, 2) for c, v in effective_sources.items()
            },
            "producing_lands": dict(producing_lands),

            "multicolor_land_count": multicolor_lands,
            "total_lands": self.analysis["counts"]["lands"],

            "note": (
                "Fractional sources reflect how lands are shared across colors. "
                "Producing lands count each land once for every color it can produce."
            )
        }


    # ======================
    # Castability
    # ======================

    def castability_snapshot(self):
        spells_by_color = defaultdict(list)

        for name in self.deck.cards:
            card = fetch_card_data(name)
            if card.get("type_line", "").lower().startswith("land"):
                continue

            cmc = int(card.get("cmc", 0))
            colors = {c for c in card.get("mana_cost", "") if c in "WUBRG"}

            for c in colors:
                spells_by_color[c].append((name, cmc))

        snapshot = []

        for color, spells in spells_by_color.items():
            name, cmc = max(spells, key=lambda x: x[1])
            sources = int(self.analysis["mana_sources"].get(color, 0))

            prob = at_least_one(
                N=len(self.deck.cards),
                K=sources,
                n=cmc + 1
            )

            snapshot.append({
                "card": name,
                "turn": cmc,
                # ✅ restore expected key
                "probability": round(prob, 3)
            })

        return snapshot

    # ======================
    # Consistency & Variance
    # ======================

    def consistency_profile(self):
        lands = self.analysis["counts"]["lands"]
        deck_size = len(self.deck.cards)

        # probabilities (0–1), NOT percentages
        miss_2_lands_t2 = 1 - at_least(2, deck_size, lands, 8)
        miss_3_lands_t3 = 1 - at_least(3, deck_size, lands, 10)

        return {
            "expected_lands_turn_4": round((lands / deck_size) * 10, 2),

            # ✅ store as probabilities
            "mana_screw_risk": round(miss_2_lands_t2, 3),
            "mana_stall_risk": round(miss_3_lands_t3, 3),

            "note": (
                "Mana screw is defined as missing your second land by turn 2. "
                "Mana stall is missing your third land by turn 3."
            )
        }


    # ======================
    # Summary
    # ======================

    def summary(self):
        colors = " • ".join(self.analysis["commander"]["color_identity"])

        return (
            f"This is a {colors}-colored deck with {self.analysis['counts']['lands']} lands "
            f"and an average mana value of {self.identity()['avg_mana_value']}. "
            f"The profile emphasizes how reliably the deck functions over many games, "
            f"not how explosive individual draws can be."
        )
