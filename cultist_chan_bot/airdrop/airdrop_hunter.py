"""Airdrop hunting logic."""

from __future__ import annotations

import json
from pathlib import Path
from ..core.logger import get_logger

import aiohttp

from ..llm import generate_reply
from ..core.db import log_airdrop
from .airdrop import save_airdrop_history

from time import time

PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "airdrop_selector.txt"


async def evaluate_airdrops(
    drops: list[dict],
    session: aiohttp.ClientSession | None = None,
) -> list[dict]:
    """Return drops recommended by TinyLlama."""
    template = PROMPT_FILE.read_text()
    prompt = f"{template}\n{json.dumps(drops)}"
    reply = await generate_reply(prompt, session=session)

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


async def join_airdrop(drop: dict) -> dict:
    """Simulate joining an airdrop and report success."""
    name = drop.get("name", "unknown")
    get_logger(__name__).info("Joining airdrop: %s", name)
    await log_airdrop(drop, "joined")
    save_airdrop_history(name, "joined", time())

    return {"name": name, "success": True}

