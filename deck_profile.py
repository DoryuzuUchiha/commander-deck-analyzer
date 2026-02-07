from collections import Counter, defaultdict
from hypergeom import at_least, at_least_one


class DeckProfile:
    def __init__(self, deck, analysis):
        self.deck = deck
        self.analysis = analysis
        self.cards = deck.card_data  # pre-fetched card data

    def build(self):
        consistency = self.consistency_profile()

        return {
            "identity": self.identity(),
            "color_demand": self.color_demand(),
            "mana_supply": self.mana_supply(),
            "castability": self.castability_snapshot(),

            "consistency": consistency,

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

        for card in self.cards.values():
            if not card["type_line"].lower().startswith("land"):
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
        }

    # ======================
    # Color Demand
    # ======================

    def color_demand(self):
        pip_counts = Counter()

        for card in self.cards.values():
            for c in card.get("mana_cost", ""):
                if c in "WUBRG":
                    pip_counts[c] += 1

        return {"pips": dict(pip_counts)}

    # ======================
    # Mana Supply
    # ======================

    def mana_supply(self):
        producing_lands = Counter()
        effective_sources = Counter()

        for card in self.cards.values():
            if not card["type_line"].lower().startswith("land"):
                continue

            produced = card.get("produced_mana", [])
            if not produced:
                continue

            for c in produced:
                producing_lands[c] += 1
                effective_sources[c] += 1 / len(produced)

        return {
            "producing_lands": dict(producing_lands),
            "effective_sources": {c: round(v, 2) for c, v in effective_sources.items()},
        }

    # ======================
    # Castability
    # ======================

    def castability_snapshot(self):
        snapshot = []

        for color in self.analysis["mana_sources"]:
            sources = self.analysis["mana_sources"][color]
            prob = at_least_one(
                N=len(self.deck.cards),
                K=sources,
                n=4
            )
            snapshot.append({
                "color": color,
                "probability": round(prob, 3)
            })

        return snapshot

    # ======================
    # Consistency (FAST ONLY)
    # ======================

    def consistency_profile(self):
        lands = self.analysis["counts"]["lands"]
        deck_size = len(self.deck.cards)

        miss_2_lands_t2 = 1 - at_least(2, deck_size, lands, 8)
        miss_3_lands_t3 = 1 - at_least(3, deck_size, lands, 10)

        return {
            "expected_lands_turn_4": round((lands / deck_size) * 10, 2),
            "mana_screw_risk": round(miss_2_lands_t2, 3),
            "mana_stall_risk": round(miss_3_lands_t3, 3),
        }

    # ======================
    # Summary
    # ======================

    def summary(self):
        colors = " • ".join(self.analysis["commander"]["color_identity"])
        return (
            f"{colors}-colored deck with "
            f"{self.analysis['counts']['lands']} lands "
            f"and average mana value "
            f"{self.identity()['avg_mana_value']}."
        )
