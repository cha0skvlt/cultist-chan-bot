"""Persona interaction utilities."""

from __future__ import annotations

import json
from pathlib import Path

import aiohttp

from .llm import generate_reply
from ..core.db import log_telemetry
from .memory import save_interaction, retrieve_context

PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "telegram_reply.txt"


async def generate_persona_reply(
    event_type: str,
    context: dict,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return TinyLlama-formatted persona reply."""
    template = PROMPT_FILE.read_text()
    payload = json.dumps({"event": event_type, "context": context})

    user_id = context.get("user_id")
    history = ""
    if user_id is not None:
        memory = retrieve_context(user_id)
        if memory:
            parts = [f"User: {m['message']}\nBot: {m['reply']}" for m in memory]
            history = "\n".join(parts)

    parts = [template]
    if history:
        parts.append(history)
    parts.append(payload)
    prompt = "\n".join(parts)

    response = await generate_reply(prompt, session=session)
    await log_telemetry(event_type, context, response)
    if user_id is not None:
        message = context.get("text") or context.get("message") or ""
        save_interaction(user_id, message, response)
    return response

