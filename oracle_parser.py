import re
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class Effect:
    category: str
    amount: Optional[int]
    repeatable: bool
    conditional: bool
    trigger: Optional[str]
    notes: str


@dataclass
class CommanderIntent:
    primary: str
    secondary: List[str]
    explanation: str


def normalize(text: str) -> str:
    return (
        text.lower()
        .replace("—", "-")
        .replace(",", "")
    )


# -------------------------
# MANA COST PARSER
# -------------------------

MANA_SYMBOL_RE = re.compile(r"\{([WUBRGC])\}")

def parse_mana_cost(mana_cost: str) -> Dict[str, int]:
    if not mana_cost:
        return {}

    pips = {}
    for symbol in MANA_SYMBOL_RE.findall(mana_cost):
        pips[symbol] = pips.get(symbol, 0) + 1

    return pips


# -------------------------
# DRAW PARSER
# -------------------------

DRAW_TRIGGERS = {
    "whenever you attack": "attack",
    "whenever .* deals combat damage": "combat_damage",
    "at the beginning of your upkeep": "upkeep",
    "whenever you cast": "cast",
}

def parse_draw(text: str) -> List[Effect]:
    t = normalize(text)
    effects = []

    if "draw" not in t:
        return effects

    amount = None
    if match := re.search(r"draw (\d+) cards", t):
        amount = int(match.group(1))
    elif "draw a card" in t:
        amount = 1

    repeatable = "whenever" in t or "at the beginning" in t
    conditional = "if" in t or "whenever" in t

    trigger = None
    for pattern, trig in DRAW_TRIGGERS.items():
        if re.search(pattern, t):
            trigger = trig
            break

    effects.append(
        Effect(
            category="draw",
            amount=amount,
            repeatable=repeatable,
            conditional=conditional,
            trigger=trigger,
            notes="oracle draw effect"
        )
    )

    return effects


# -------------------------
# RAMP PARSER
# -------------------------

RAMP_PATTERNS = [
    r"search your library for a .* land",
    r"put .* land onto the battlefield",
    r"add \{[wubrgc]\}",
]

RAMP_TRIGGERS = {
    "whenever a land enters": "landfall",
    "at the beginning of your upkeep": "upkeep",
}

def parse_ramp(text: str) -> List[Effect]:
    t = normalize(text)
    effects = []

    if not any(re.search(p, t) for p in RAMP_PATTERNS):
        return effects

    repeatable = "whenever" in t or "at the beginning" in t
    conditional = "if" in t or "whenever" in t

    trigger = None
    for phrase, trig in RAMP_TRIGGERS.items():
        if phrase in t:
            trigger = trig
            break

    effects.append(
        Effect(
            category="ramp",
            amount=None,
            repeatable=repeatable,
            conditional=conditional,
            trigger=trigger,
            notes="oracle ramp effect"
        )
    )

    return effects


def parse_oracle(text: str) -> List[Effect]:
    effects = []
    effects.extend(parse_draw(text))
    effects.extend(parse_ramp(text))
    return effects


COMMANDER_PATTERNS = {
    "aristocrats": ["whenever a creature dies", "sacrifice a creature"],
    "spellslinger": ["whenever you cast a noncreature spell", "instant or sorcery"],
    "combat": ["whenever you attack", "combat damage"],
    "tokens": ["create .* token"],
    "landfall": ["whenever a land enters"],
    "draw_matters": ["whenever you draw a card"],
}

def analyze_commander(text: str) -> CommanderIntent:
    t = normalize(text)
    matched = []

    for strategy, patterns in COMMANDER_PATTERNS.items():
        for p in patterns:
            if re.search(p, t):
                matched.append(strategy)
                break

    primary = matched[0] if matched else "generic_value"
    secondary = matched[1:]

    explanation = (
        f"Commander rewards {', '.join(matched)}"
        if matched else
        "Commander provides general value"
    )

    return CommanderIntent(
        primary=primary,
        secondary=secondary,
        explanation=explanation
    )
