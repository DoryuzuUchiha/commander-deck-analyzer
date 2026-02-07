from flask import Flask, render_template, request
from deck import Deck
from deck_parser import parse_deck
from scryfall import fetch_cards_bulk
from capabilities import extract_capabilities
from deck_profile import DeckProfile
from mulligans import run_mulligan_simulation

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", analysis=None, profile=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    decklist = request.form.get("decklist", "")

    flat_cards, unique_cards, commander_name = parse_deck(decklist)

    card_data_map = fetch_cards_bulk(unique_cards)

    commander_card = card_data_map.get(commander_name.lower())
    if not commander_card:
        raise RuntimeError(f"Commander not found: {commander_name}")

    card_capabilities = {}
    for name in unique_cards:
        card_data = card_data_map.get(name.lower())
        if card_data:
            card_capabilities[name] = extract_capabilities(card_data)

    deck = Deck(flat_cards, commander_card)
    deck.card_capabilities = card_capabilities
    deck.card_data = card_data_map

    analysis = deck.analyze()
    profile = DeckProfile(deck, analysis).build()

    return render_template(
        "index.html",
        analysis=analysis,
        profile=profile,
        decklist=decklist
    )


@app.route("/mulligans", methods=["POST"])
def mulligans():
    decklist = request.form.get("decklist", "")

    flat_cards, unique_cards, commander_name = parse_deck(decklist)
    card_data_map = fetch_cards_bulk(unique_cards)

    commander_card = card_data_map.get(commander_name.lower())
    if not commander_card:
        raise RuntimeError(f"Commander not found: {commander_name}")

    card_capabilities = {}
    for name in unique_cards:
        card_data = card_data_map.get(name.lower())
        if card_data:
            card_capabilities[name] = extract_capabilities(card_data)

    deck = Deck(flat_cards, commander_card)
    deck.commander_colors = set(commander_card.get("color_identity", []))
    deck.card_capabilities = card_capabilities
    deck.card_data = card_data_map

    # 🔥 ONLY NOW do we run simulations
    results = run_mulligan_simulation(deck)
    results["decklist"] = decklist
    
    return render_template(
        "mulligans.html",
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)
