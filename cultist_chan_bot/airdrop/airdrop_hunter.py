"""Airdrop hunting logic."""

from __future__ import annotations

import json
from pathlib import Path
from .logger import get_logger

import asyncio

from .llm import query_llm
from .db import log_airdrop
from .airdrop import save_airdrop_history

from time import time

PROMPT_FILE = Path(__file__).with_name("prompts") / "airdrop_selector.txt"


def evaluate_airdrops(drops: list[dict]) -> list[dict]:
    """Return drops recommended by TinyLlama."""
    template = PROMPT_FILE.read_text()
    prompt = f"{template}\n{json.dumps(drops)}"
    reply = asyncio.run(query_llm(prompt))

    try:
        parsed = json.loads(reply)
    except json.JSONDecodeError:
        parsed = [p.strip() for p in reply.replace(",", "\n").splitlines() if p.strip()]
    results: list[dict] = []
    if all(isinstance(x, int) for x in parsed):
        for i in parsed:
            if 0 <= i < len(drops):
                results.append(drops[i])
    else:
        names = {d.get("name") for d in drops}
        for name in parsed:
            if name in names:
                results.extend(d for d in drops if d.get("name") == name)
    return results


def join_airdrop(drop: dict) -> dict:
    """Simulate joining an airdrop and report success."""
    name = drop.get("name", "unknown")
    get_logger(__name__).info("Joining airdrop: %s", name)
    log_airdrop(drop, "joined")
    save_airdrop_history(name, "joined", time())

    return {"name": name, "success": True}

