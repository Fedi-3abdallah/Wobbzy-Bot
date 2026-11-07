from flask import Flask, render_template, request, jsonify, session

from google import genai
import os

_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
previous_interaction_id = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chatbot():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        previous_interaction_id = session.get("previous_interaction_id")

        if previous_interaction_id:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=message,
                previous_interaction_id=previous_interaction_id,
            )
        else:
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=message,
            )

        session["previous_interaction_id"] = interaction.id
        return jsonify({"response": interaction.output_text})

    except Exception as e:
        error_text = str(e).lower()
        status_code = getattr(e, "status_code", None) or getattr(e, "code", None)

        quota_exhausted = status_code == 429 or any(
            marker in error_text
            for marker in (
                "resource_exhausted",
                "quota exceeded",
                "quota has been exceeded",
                "rate limit exceeded",
            )
        )

        if quota_exhausted:
            return (
                jsonify(
                    {
                        "code": "quota_exhausted",
                        "error": "The free AI token limit has been reached. Please try again later.",
                    }
                ),
                429,
            )

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
