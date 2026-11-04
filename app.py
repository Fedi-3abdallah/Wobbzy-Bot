import os

from flask import Flask, jsonify, render_template, request, session
from google import genai

_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

app = Flask(__name__)

secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your environment or .env file.")

app.secret_key = secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in your environment or .env file.")

client = genai.Client(api_key=api_key)
model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chatbot():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request must contain a JSON object"}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    message = message.strip()
    if len(message) > 10_000:
        return jsonify({"error": "Message is too long"}), 400

    try:
        previous_interaction_id = session.get("gemini_interaction_id")

        request_args = {
            "model": model,
            "input": message,
        }
        if previous_interaction_id:
            request_args["previous_interaction_id"] = previous_interaction_id

        interaction = client.interactions.create(**request_args)

        session["gemini_interaction_id"] = interaction.id

        return jsonify({"response": interaction.output_text})

    except Exception:
        app.logger.exception("Gemini request failed")
        return jsonify({"error": "The bot couldn't respond. Please try again."}), 500


@app.route("/reset-chat", methods=["POST"])
def reset_chat():
    session.pop("gemini_interaction_id", None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=False)
