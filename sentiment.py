"""Lightweight sentiment engine with an optional Hugging Face Transformers model.

Default mode is a small offline lexicon-based baseline so the app deploys easily
on low-memory hosting. Set USE_TRANSFORMERS=1 to load a Transformers model;
that downloads model weights at startup and requires more RAM and disk.
"""
import os
import re

POSITIVE = {
    "amazing", "awesome", "best", "brilliant", "comfortable", "delightful",
    "easy", "excellent", "fantastic", "fast", "friendly", "good", "great",
    "happy", "helpful", "impressive", "love", "loved", "lovely", "perfect",
    "recommend", "smooth", "satisfied", "thank", "thanks", "useful", "wonderful",
    "worth", "beautiful", "enjoy", "enjoyed", "reliable", "nice", "positive"
}
NEGATIVE = {
    "awful", "bad", "boring", "broken", "buggy", "complaint", "disappointed",
    "disappointing", "hate", "hated", "horrible", "late", "poor", "problem",
    "refund", "rude", "slow", "terrible", "unhappy", "useless", "waste",
    "worst", "wrong", "negative", "expensive", "dirty", "crash", "crashes",
    "failed", "failure", "annoying", "return"
}
NEGATIONS = {"not", "never", "no", "hardly", "isn't", "wasn't", "don't", "didn't", "can't"}
INTENSIFIERS = {"very", "really", "extremely", "so", "too"}

_transformer = None
_transformer_error = None

def _transformer_result(text):
    global _transformer, _transformer_error
    if os.getenv("USE_TRANSFORMERS", "0").lower() not in ("1", "true", "yes"):
        return None
    try:
        if _transformer is None:
            from transformers import pipeline
            model_name = os.getenv("SENTIMENT_MODEL", "distilbert/distilbert-base-uncased-finetuned-sst-2-english")
            _transformer = pipeline("sentiment-analysis", model=model_name)
        raw = _transformer(text[:2000])[0]
        label = raw["label"].upper()
        score = float(raw["score"])
        if label in ("POSITIVE", "LABEL_1"):
            sentiment = "Positive"
        elif label in ("NEGATIVE", "LABEL_0"):
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        return {
            "sentiment": sentiment,
            "score": round(score * 100, 1),
            "method": "Hugging Face Transformers",
            "positive_words": [],
            "negative_words": [],
            "explanation": f"Model confidence: {score:.1%}. This is a prediction, not a guarantee."
        }
    except Exception as exc:
        _transformer_error = str(exc)
        return None

def analyze_sentiment(text):
    transformer = _transformer_result(text)
    if transformer:
        return transformer

    words = re.findall(r"[a-z']+", text.lower())
    pos_hits, neg_hits = [], []
    score = 0
    for i, word in enumerate(words):
        weight = 2 if i > 0 and words[i - 1] in INTENSIFIERS else 1
        negated = i > 0 and words[i - 1] in NEGATIONS
        if word in POSITIVE:
            (neg_hits if negated else pos_hits).append(word)
            score += -weight if negated else weight
        elif word in NEGATIVE:
            (pos_hits if negated else neg_hits).append(word)
            score += weight if negated else -weight

    if score > 0:
        label = "Positive"
    elif score < 0:
        label = "Negative"
    else:
        label = "Neutral"
    confidence = min(98.0, 50.0 + abs(score) * 8.0)
    if not pos_hits and not neg_hits:
        explanation = "No strong words from the demo sentiment vocabulary were detected. Neutral does not necessarily mean emotion-free."
    else:
        explanation = f"Detected {len(pos_hits)} positive and {len(neg_hits)} negative cue(s). Context, sarcasm, and language can affect accuracy."
    return {
        "sentiment": label,
        "score": round(confidence, 1),
        "method": "Lexicon baseline (offline demo)",
        "positive_words": pos_hits,
        "negative_words": neg_hits,
        "explanation": explanation
    }
