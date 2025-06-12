"""TinyLlama interface."""


from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .config import load_config

_CFG = load_config()


async def query_llm(prompt: str) -> str:
    """Return TinyLlama result for the given prompt."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _CFG.LLM_URL,
                json={"prompt": prompt},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                data: Any = await resp.json()
                return str(data.get("response", "")).strip()
    except asyncio.TimeoutError as e:
        raise RuntimeError("LLM request timed out") from e
    except aiohttp.ClientError as e:
        raise RuntimeError(f"LLM request failed: {e}") from e
