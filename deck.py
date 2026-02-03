BASIC_LANDS = {
    "Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"
}

COLOR_SYMBOLS = {"W", "U", "B", "R", "G"}


class Card:
    def __init__(self, name, count=1):
        self.name = name
        self.count = count


class Deck:
    def __init__(self, parsed_cards, commander_name):
        self.cards = [Card(name, count) for count, name in parsed_cards]
        self.capabilities = {}

        self.commander_name = commander_name
        self.commander_cmc = None
        self.commander_colors = set()

    def set_commander_capabilities(self, caps, cmc):
        self.commander_cmc = cmc
        self.commander_colors = {
            c for c in caps.get("color_identity", [])
            if c in COLOR_SYMBOLS
        }

    def add_card_capabilities(self, name, caps):
        self.capabilities[name] = caps

    def basic_land_count(self):
        return sum(c.count for c in self.cards if c.name in BASIC_LANDS)

    def nonbasic_land_count(self):
        return sum(
            c.count for c in self.cards
            if c.name not in BASIC_LANDS
            and "land" in self.capabilities.get(c.name, {}).get("types", [])
        )

    def total_land_count(self):
        return self.basic_land_count() + self.nonbasic_land_count()

    def analyze(self):
        from analysis import (
            count_ramp,
            count_burst_draw,
            count_draw_engines,
            list_repeatable_ramp,
            list_burst_draw,
            list_draw_engines,
            commander_on_curve_probability,
            mana_sources_by_color,
            color_saturation,
            ideal_color_sources,
            simulate_mulligans,
            simulate_early_game,
            deck_summary_score,
            optimize_deck
        )

        print("\nDeck Analysis")
        print("------------")
        print(f"Commander: {self.commander_name}")
        print(f"Commander colors: {''.join(sorted(self.commander_colors))}")
        print(f"Lands: {self.total_land_count()}")

        print("\nRepeatable Ramp:")
        for c in list_repeatable_ramp(self):
            print(f"  - {c}")

        print("\nBurst Draw:")
        for c in list_burst_draw(self):
            print(f"  - {c}")

        print("\nRepeatable Draw Engines:")
        for c in list_draw_engines(self):
            print(f"  - {c}")

        print(f"\nCommander on-curve probability: {commander_on_curve_probability(self):.1f}%")

        print("\nMana sources by color:")
        sources = mana_sources_by_color(self)
        for c, n in sources.items():
            print(f"  {c}: {n}")

        print("\nColor Saturation:")
        sat = color_saturation(self)
        for c, pct in sat["percentages"].items():
            print(f"  {c}: {pct:.1f}%")

        print("\nIdeal Mana Sources:")
        ideal = ideal_color_sources(self, sum(sources.values()))
        for c, n in ideal.items():
            print(f"  {c}: {n}")

        print("\nMulligan Simulation (10k runs):")
        for k, v in simulate_mulligans(self).items():
            print(f"  {k}: {v:.2f}")

        print("\nEarly Game Consistency (Turns 1–3):")
        early = simulate_early_game(self)
        for k, v in early.items():
            print(f"  {k}: {v:.1f}%")
        print("\nDeck Consistency Score:")
        score = deck_summary_score(self)

        print(f"  Total Score: {score['total_score']} / 100")
        print(f"    Mulligans: {score['mulligan_score']}/25")
        print(f"    Land drops: {score['land_score']}/25")
        print(f"    Early plays: {score['play_score']}/25")
        print(f"    Color stability: {score['color_score']}/25")

        if score["total_score"] >= 85:
            tier = "Excellent"
        elif score["total_score"] >= 70:
            tier = "Good"
        elif score["total_score"] >= 55:
            tier = "Playable"
        else:
            tier = "Inconsistent"

        print(f"  Tier: {tier}")

        print("\nOptimization Recommendations")
        print("----------------------------")

        opt = optimize_deck(self)

        print(f"Primary Issue: {opt['primary_issue']}")

        if opt["issues"]:
            print("\nProblems Detected:")
            for i in opt["issues"]:
                print(f"  - {i}")

        if opt["improvements"]:
            print("\nRecommended Improvements:")
            for r in opt["improvements"]:
                print(f"  - {r}")

        if opt["suggested_cuts"]:
            print("\nSuggested Cuts (Theoretical):")
            for c in opt["suggested_cuts"]:
                print(f"  - {c}")

