"""TinyLlama interface."""


from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from ..core.config import load_config

_CFG = load_config()


async def generate_reply(
    prompt: str,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return TinyLlama result for the given prompt."""

    async def _post(sess: aiohttp.ClientSession) -> str:
        async with sess.post(
            _CFG.LLM_URL,
            json={"prompt": prompt},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            data: Any = await resp.json()
            return str(data.get("response", "")).strip()

    try:
        if session is None:
            async with aiohttp.ClientSession() as sess:
                return await _post(sess)
        return await _post(session)
    except asyncio.TimeoutError as e:
        raise RuntimeError("LLM request timed out") from e
    except aiohttp.ClientError as e:
        raise RuntimeError(f"LLM request failed: {e}") from e


query_llm = generate_reply
