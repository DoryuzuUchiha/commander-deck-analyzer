from flask import Flask, render_template, request
from deck import Deck
from deck_parser import parse_deck
from capabilities import fetch_card_data, extract_capabilities
from deck_profile import DeckProfile   # ✅ NEW

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", analysis=None, profile=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    decklist = request.form.get("decklist", "")
    cards, commander_name = parse_deck(decklist)

    # Fetch commander card object
    commander_card = fetch_card_data(commander_name)

    # Build capabilities for all cards in the deck
    card_capabilities = {}
    for card_name in set(cards):
        card = fetch_card_data(card_name)
        card_capabilities[card_name] = extract_capabilities(card)

    # Create deck and inject capabilities
    deck = Deck(cards, commander_card)
    deck.card_capabilities = card_capabilities

    # Existing analysis (KEEP)
    analysis = deck.analyze()

    # ✅ NEW: Build deck profile
    profile = DeckProfile(deck, analysis).build()

    return render_template(
        "index.html",
        analysis=analysis,
        profile=profile
    )


if __name__ == "__main__":
    app.run(debug=True)
