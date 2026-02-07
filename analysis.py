import os
import json
import random
from math import comb, ceil

COLOR_SYMBOLS = {"W", "U", "B", "R", "G"}


# ==================================================
# Deck cache helpers
# ==================================================

def get_deck_cache_dir(deck):
    safe_name = deck.commander_name.replace(" ", "_")
    return os.path.join("cache", "decks", safe_name)


# ==================================================
# Count helpers
# ==================================================

def count_ramp(deck):
    return len(list_repeatable_ramp(deck))


def count_burst_draw(deck):
    return len(list_burst_draw(deck))


def count_draw_engines(deck):
    return len(list_draw_engines(deck))


# ==================================================
# Commander on-curve probability
# ==================================================

def commander_on_curve_probability(deck):
    if deck.commander_cmc is None:
        return 0.0

    cmc_required = int(ceil(deck.commander_cmc))

    total_lands = deck.total_land_count()
    ramp = count_ramp(deck)

    effective_sources = total_lands + ramp
    draws = 7 + cmc_required - 1
    deck_size = 99

    def hypergeom_at_least(k, N, K, n):
        return sum(
            comb(K, i) * comb(N - K, n - i) / comb(N, n)
            for i in range(k, min(n, K) + 1)
        )

    return hypergeom_at_least(
        cmc_required,
        deck_size,
        effective_sources,
        draws
    ) * 100


# ==================================================
# Utilities
# ==================================================

def _extract_mana_symbols(mana_cost):
    if not mana_cost:
        return []
    return [
        p for p in mana_cost.replace("}", "").split("{")
        if p in COLOR_SYMBOLS
    ]


def _build_flat_deck(deck):
    """
    Deck.cards is already a flat list of card names.
    """
    return list(deck.cards)


# ==================================================
# Color saturation (spell demand)
# ==================================================

def color_saturation(deck):
    counts = {c: 0 for c in COLOR_SYMBOLS}

    for name in deck.cards:
        card = deck.card_data.get(name.lower())
        if not card:
            continue

        if "land" in card.get("type_line", "").lower():
            continue

        for s in _extract_mana_symbols(card.get("mana_cost", "")):
            counts[s] += 1

    total = sum(counts.values())
    return {
        "counts": counts,
        "percentages": {
            c: (counts[c] / total * 100) if total else 0
            for c in counts
        },
        "total_symbols": total
    }


# ==================================================
# Mana sources
# ==================================================

def mana_sources_by_color(deck, include_tapped=False):
    colors = {c: 0 for c in ["W", "U", "B", "R", "G", "C"]}

    for name in deck.cards:
        caps = deck.card_capabilities.get(name, {})

        for mana in caps.get("mana", []):
            if (
                mana.get("source") == "land"
                and mana.get("enters_tapped")
                and not include_tapped
            ):
                continue

            produces = mana.get("produces", [])

            if set(produces) >= {"W", "U", "B", "R", "G"}:
                produces = deck.commander_colors

            for c in produces:
                if c in colors:
                    colors[c] += 1

    return colors


def ideal_color_sources(deck, total_sources):
    sat = color_saturation(deck)
    return {
        c: round((pct / 100) * total_sources)
        for c, pct in sat["percentages"].items()
    }


# ==================================================
# Category lists
# ==================================================

def list_repeatable_ramp(deck):
    cards = []
    for name in deck.cards:
        caps = deck.card_capabilities.get(name, {})
        if "land" in caps.get("types", []):
            continue
        for mana in caps.get("mana", []):
            if mana.get("repeatable"):
                cards.append(name)
                break
    return cards


def list_burst_draw(deck, min_cards=2):
    cards = []
    for name in deck.cards:
        for draw in deck.card_capabilities.get(name, {}).get("draw", []):
            if isinstance(draw.get("amount"), int) and draw["amount"] >= min_cards:
                cards.append(name)
                break
    return cards


def list_draw_engines(deck):
    cards = []
    for name in deck.cards:
        for draw in deck.card_capabilities.get(name, {}).get("draw", []):
            if draw.get("amount") == 1 and draw.get("conditional"):
                cards.append(name)
                break
    return cards


# ==================================================
# Mulligan simulation
# ==================================================

def _hand_stats(hand, deck):
    lands = 0
    colors = set()
    has_ramp = False

    for name in hand:
        caps = deck.card_capabilities.get(name, {})

        if "land" in caps.get("types", []):
            lands += 1

        for mana in caps.get("mana", []):
            produces = mana.get("produces", [])
            if set(produces) >= {"W", "U", "B", "R", "G"}:
                produces = deck.commander_colors

            for c in produces:
                if c in deck.commander_colors:
                    colors.add(c)

            if mana.get("repeatable") and "land" not in caps.get("types", []):
                has_ramp = True

    return lands, colors, has_ramp


def _is_keepable(hand, deck):
    lands, colors, has_ramp = _hand_stats(hand, deck)

    if lands == 0 or lands >= 6:
        return False
    if lands == 1 and not has_ramp:
        return False
    if not deck.commander_colors.issubset(colors):
        return False

    return True


def simulate_mulligans(deck, iterations=10_000):
    flat = _build_flat_deck(deck)

    keep_7 = mull_1 = mull_2 = mull_3p = total = 0

    for _ in range(iterations):
        mulls = 0
        while mulls <= 3:
            random.shuffle(flat)
            if _is_keepable(flat[:7], deck):
                break
            mulls += 1

        total += mulls
        if mulls == 0:
            keep_7 += 1
        elif mulls == 1:
            mull_1 += 1
        elif mulls == 2:
            mull_2 += 1
        else:
            mull_3p += 1

    return {
        "keep_7_pct": keep_7 / iterations * 100,
        "mull_1_pct": mull_1 / iterations * 100,
        "mull_2_pct": mull_2 / iterations * 100,
        "mull_3_plus_pct": mull_3p / iterations * 100,
        "avg_mulls": total / iterations
    }


# ==================================================
# Early game consistency
# ==================================================

def simulate_early_game(deck, iterations=10_000):
    flat = _build_flat_deck(deck)

    t1_land = t2_land = t3_land = 0
    t1_play = t2_play = t3_play = 0
    color_fail_t2 = color_fail_t3 = 0

    for _ in range(iterations):
        while True:
            random.shuffle(flat)
            hand = flat[:7]
            if _is_keepable(hand, deck):
                break

        library = flat[7:]
        lands = 0
        colors = set()

        for turn in [1, 2, 3]:
            if library:
                hand.append(library.pop(0))

            for c in list(hand):
                caps = deck.card_capabilities.get(c, {})
                if "land" in caps.get("types", []):
                    hand.remove(c)
                    lands += 1
                    for mana in caps.get("mana", []):
                        produces = mana.get("produces", [])
                        if set(produces) >= {"W", "U", "B", "R", "G"}:
                            produces = deck.commander_colors
                        colors.update(produces)
                    break

            if turn == 1 and lands >= 1:
                t1_land += 1
            if turn == 2 and lands >= 2:
                t2_land += 1
            if turn == 3 and lands >= 3:
                t3_land += 1

            playable = False
            for c in hand:
                caps = deck.card_capabilities.get(c, {})
                if any(
                    m.get("repeatable") and "land" not in caps.get("types", [])
                    for m in caps.get("mana", [])
                ):
                    playable = True

                cmc = caps.get("cmc")
                if isinstance(cmc, (int, float)) and cmc <= lands:
                    playable = True

                if playable:
                    break

            if playable:
                if turn == 1:
                    t1_play += 1
                if turn == 2:
                    t2_play += 1
                if turn == 3:
                    t3_play += 1

            if turn == 2 and not deck.commander_colors.issubset(colors):
                color_fail_t2 += 1
            if turn == 3 and not deck.commander_colors.issubset(colors):
                color_fail_t3 += 1

    return {
        "t1_land_pct": t1_land / iterations * 100,
        "t2_land_pct": t2_land / iterations * 100,
        "t3_land_pct": t3_land / iterations * 100,
        "t1_play_pct": t1_play / iterations * 100,
        "t2_play_pct": t2_play / iterations * 100,
        "t3_play_pct": t3_play / iterations * 100,
        "color_screw_t2_pct": color_fail_t2 / iterations * 100,
        "color_screw_t3_pct": color_fail_t3 / iterations * 100
    }
