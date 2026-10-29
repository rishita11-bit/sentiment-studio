# Sentiment Studio — AI-Based Sentiment Analyzer

A responsive Flask web app for analyzing product reviews, customer feedback, and social comments. It classifies text as Positive, Negative, or Neutral and shows a score plus detected word cues.

## Features
- Mobile-friendly interface
- Form and JSON API (`POST /api/analyze`)
- Health endpoint (`GET /health`)
- Offline lexicon baseline, so it runs on low-cost hosting
- Optional Hugging Face Transformers model mode

## Tech stack
Python, Flask, HTML/CSS/JavaScript, optional Hugging Face Transformers.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux/Android terminal: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Optional Transformers mode
Install a compatible PyTorch build and Transformers, then set `USE_TRANSFORMERS=1`. The first run downloads model weights and needs more memory; for a simple phone-hosted demo, leave it off. The default lexicon mode is a baseline, not a state-of-the-art model. Be transparent about this in a presentation.

## Deploy on Render
1. Push this folder to a GitHub repository.
2. In Render, create a **New Web Service** and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy; open the public URL and test both the home page and `/health`.

`render.yaml` is included as a starting configuration. Hosting providers can change their free-plan terms.

## API example
```bash
curl -X POST https://YOUR-APP-URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"The service was excellent and fast"}'
```

## Limitations
The default analyzer uses a small English cue-word vocabulary. It can misread sarcasm, mixed feelings, negation, slang, and non-English text. Do not present the score as a calibrated probability.
