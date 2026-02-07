from oracle_parser import analyze_commander, parse_mana_cost
from simulations import simulate_mulligans


class Deck:
    def __init__(self, cards, commander):
        if isinstance(commander, list):
            commander = commander[0]

        self.cards = cards
        self.commander = commander
        self.card_capabilities = {}
        self.commander_intent = None

        self._analyze_commander()

    def _analyze_commander(self):
        oracle = self.commander.get("oracle_text", "")
        self.commander_intent = analyze_commander(oracle)



    def add_card_capabilities(self, name, caps):
        self.card_capabilities[name] = caps

    def analyze(self):
        lands = 0
        ramp = 0
        cantrips = 0
        burst_draw = 0
        draw_engines = 0

        commander_colors = set(self.commander.get("color_identity", []))

        # 🔹 LAND-ONLY mana sources (tap-based)
        mana_sources = {c: 0 for c in commander_colors}
        mana_demand = {c: 0 for c in commander_colors}

        for name in self.cards:
            caps = self.card_capabilities.get(name, {})
            card = caps.get("card", {})

            is_land = "land" in caps.get("types", [])

            # ---------- LAND COUNT ----------
            if is_land:
                lands += 1

                # Count how many colors this land can tap for
                produces = set()
                for src in caps.get("mana", []):
                    produces.update(src.get("produces", []))

                for c in produces:
                    if c in mana_sources:
                        mana_sources[c] += 1

            # ---------- RAMP (unchanged) ----------
            if not is_land and caps.get("mana"):
                ramp += 1

            # ---------- DRAW ----------
            for d in caps.get("draw", []):
                if d["category"] == "cantrip":
                    cantrips += 1
                elif d["category"] == "burst":
                    burst_draw += 1
                elif d["category"] == "engine":
                    draw_engines += 1

            # ---------- MANA SATURATION ----------
            pip_counts = parse_mana_cost(card.get("mana_cost", ""))
            for color, count in pip_counts.items():
                if color in mana_demand:
                    mana_demand[color] += count

        # ---------- SATURATION MATH ----------
        total_pips = sum(mana_demand.values())

        if total_pips == 0:
            saturation_percentages = {c: 0 for c in commander_colors}
            ideal_distribution = {c: 0 for c in commander_colors}
            ideal_land_counts = {c: 0 for c in commander_colors}
        else:
            saturation_percentages = {
                c: round((mana_demand[c] / total_pips) * 100)
                for c in commander_colors
            }

            ideal_distribution = dict(saturation_percentages)

            ideal_land_counts = {
                c: round((mana_demand[c] / total_pips) * lands)
                for c in commander_colors
            }

        mulligans = simulate_mulligans(
            cards=self.cards,
            card_capabilities=self.card_capabilities,
            color_identity=list(commander_colors),
            simulations=5000
        )

        return {
            "commander": {
                "name": self.commander.get("name"),
                "color_identity": list(commander_colors),
                "playstyle": self.commander_intent.primary,
                "explanation": self.commander_intent.explanation,
            },
            "counts": {
                "lands": lands,
                "ramp": ramp,
                "cantrips": cantrips,
                "burst_draw": burst_draw,
                "draw_engines": draw_engines,
            },

            # 🔹 ACTUAL land taps
            "mana_sources": mana_sources,

            # 🔹 SPELL DEMAND
            "mana_saturation": {
                "raw": mana_demand,
                "total_pips": total_pips,
                "percentages": saturation_percentages,

                # 🔧 BACKWARD COMPATIBILITY (for existing template)
                # This is still a % and matches saturation by definition
                "ideal_distribution": dict(saturation_percentages),
            },

            # 🔹 NEW: IDEAL LAND COUNTS (what you actually want)
            "ideal_mana_sources": ideal_land_counts,

            "mulligan_simulation": mulligans,
        }
    # add to Deck class in deck.py

    def lands(self):
        return [c for c in self.cards if c.is_land()]

    def spells(self):
        return [c for c in self.cards if not c.is_land()]

    def land_count(self):
        return len(self.lands())

    def spell_count(self):
        return len(self.spells())

    def colors(self):
        colors = set()
        for card in self.spells():
            colors.update(card.colors)
        return colors

