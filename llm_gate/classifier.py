from __future__ import annotations

"""Intent classifier using local TinyLlama."""

import re
import requests

from .config import load_config

DEFAULT_URL = "http://localhost:8000/generate"


def query_llm(prompt: str, url: str = DEFAULT_URL) -> str:
    """Send prompt to TinyLlama and return response text."""
    resp = requests.post(url, json={"prompt": prompt}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return str(data.get("response", "")).strip()


def classify_request(user_input: str) -> dict:
    """Return intent classification for the given text."""
    cfg = load_config()
    intents = cfg.get("critical_intents", [])
    prompt = (
        "Does the user intend to perform any of these actions: "
        f"{', '.join(intents)}?\n{user_input}"
    )
    text = query_llm(prompt).lower()
    match = re.search(r"intent=([a-zA-Z_]+)", text)
    intent = match.group(1) if match else None
    if intent not in intents:
        intent = None
    return {"is_critical": intent is not None, "matched_intent": intent}
