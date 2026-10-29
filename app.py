import os
from flask import Flask, render_template, request, jsonify
from sentiment import analyze_sentiment

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200_000

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/analyze")
def analyze():
    text = (request.form.get("text") or "").strip()
    if not text:
        return render_template("index.html", error="Please enter a review or comment.")
    if len(text) > 5000:
        return render_template("index.html", error="Please keep the text under 5,000 characters.", text=text[:5000])
    result = analyze_sentiment(text)
    return render_template("index.html", text=text, result=result)

@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    if not text:
        return jsonify({"error": "The 'text' field is required."}), 400
    if len(text) > 5000:
        return jsonify({"error": "Text must be 5,000 characters or fewer."}), 400
    return jsonify({"text": text, **analyze_sentiment(text)})

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
