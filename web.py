from flask import Flask, render_template, request
import io
import sys

from cli import main as run_cli_analysis

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""

    if request.method == "POST":
        raw_text = request.form.get("decklist", "")

        # Remove empty lines and trim whitespace
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if len(lines) >= 2:
            cards = lines[:-1]
            commander = lines[-1]

            # Exactly one blank line before commander
            deck_text = "\n".join(cards) + "\n\n" + commander
        else:
            deck_text = "\n".join(lines)

        # Write deck.txt
        with open("deck.txt", "w", encoding="utf-8") as f:
            f.write(deck_text)

        # Capture stdout
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            run_cli_analysis()
        except Exception as e:
            output = f"ERROR:\n{e}"
        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue()

    return render_template("index.html", output=output)


if __name__ == "__main__":
    app.run(debug=True)
