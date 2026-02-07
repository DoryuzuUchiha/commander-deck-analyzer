from oracle_parser import parse_oracle


def get_tags(card):
    tags = set()

    oracle = card.get("oracle_text", "")
    effects = parse_oracle(oracle)

    for effect in effects:
        if effect.category == "draw":
            tags.add("draw")
            if effect.repeatable:
                tags.add("repeatable_draw")

        if effect.category == "ramp":
            tags.add("ramp")
            if effect.repeatable:
                tags.add("repeatable_ramp")

    # Keep your existing tag logic intact below this line
    # (artifacts, removal, etc.)

    return sorted(tags)
