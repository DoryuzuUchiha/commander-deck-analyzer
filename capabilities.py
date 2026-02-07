import re
import requests

SCRYFALL_URL = "https://api.scryfall.com/cards/named"


def fetch_card_data(name):
    resp = requests.get(SCRYFALL_URL, params={"exact": name})
    resp.raise_for_status()
    return resp.json()


def extract_capabilities(card):
    caps = {
        "types": [],
        "mana": [],
        "draw": [],
        # ✅ REQUIRED for mana saturation
        "card": {
            "mana_cost": card.get("mana_cost", "")
        }
    }

    # ---------- TYPES ----------
    type_line = card.get("type_line", "").lower()
    caps["types"] = type_line.split()

    oracle = card.get("oracle_text", "").lower()

    # ---------- MANA PRODUCTION ----------
    add_clauses = re.findall(r"add\s+([^\n\.]+)", oracle)

    for clause in add_clauses:
        produces = set()

        if "any color" in clause:
            produces.update(["W", "U", "B", "R", "G"])
        else:
            if "w" in clause: produces.add("W")
            if "u" in clause: produces.add("U")
            if "b" in clause: produces.add("B")
            if "r" in clause: produces.add("R")
            if "g" in clause: produces.add("G")
            if "c" in clause: produces.add("C")

        if produces:
            caps["mana"].append({
                "produces": list(produces)
            })

    # ---------- DRAW DETECTION ----------
    if re.search(r"draw (a|one|\d+) card", oracle):
        repeatable = any(
            kw in oracle for kw in
            ["whenever", "at the beginning", "each time"]
        )

        is_cantrip = (
            not repeatable
            and card.get("cmc", 99) <= 2
        )

        engine_type = None
        if repeatable:
            if "instant or sorcery" in oracle:
                engine_type = "spellslinger"
            elif "deals damage" in oracle:
                engine_type = "combat"
            elif "opponent" in oracle:
                engine_type = "tax"
            else:
                engine_type = "generic"

        caps["draw"].append({
            "category": (
                "engine" if repeatable else
                "cantrip" if is_cantrip else
                "burst"
            ),
            "repeatable": repeatable,
            "engine_type": engine_type,
        })

    return caps
