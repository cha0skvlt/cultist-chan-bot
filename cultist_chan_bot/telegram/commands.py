"""Telegram command handlers."""

from __future__ import annotations

from time import time
from typing import Any, Dict
import sqlite3
from pathlib import Path


from . import db

import aiohttp

from .persona import generate_persona_reply
from .airdrop_hunter import join_airdrop


ADMIN_IDS = {1}


SEEN_USERS_FILE = Path(__file__).with_name("seen_users.txt")
_SEEN_USERS: set[int] = set()

if SEEN_USERS_FILE.exists():
    for line in SEEN_USERS_FILE.read_text().splitlines():
        try:
            _SEEN_USERS.add(int(line.strip()))
        except ValueError:
            pass



async def status(
    scans: int = 0,
    purchases: int = 0,
    donations: float = 0.0,
    timestamp: float | None = None,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return persona-formatted status reply."""

    context: Dict[str, Any] = {
        "scans": scans,
        "purchases": purchases,
        "donations": donations,
        "timestamp": timestamp or time(),
    }
    return await generate_persona_reply("status", context, session=session)




async def join_airdrop_action(
    drop: dict,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Join an airdrop and return persona-formatted message."""
    result = await join_airdrop(drop)
    if result.get("success"):
        context = {"name": result.get("name"), "drop": drop}
        return await generate_persona_reply("airdrop_joined", context, session=session)
      
    return ""


async def airdrops(
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return persona-formatted airdrop history."""

    history = await db.get_airdrop_history()
    return await generate_persona_reply("airdrops_history", {"airdrops": history}, session=session)



async def log_stats(
    user_id: int,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return summary stats for admins only."""
    if user_id not in ADMIN_IDS:

        return ""
    with sqlite3.connect(db.DB_PATH) as conn:
        joined = conn.execute(
            "SELECT COUNT(*) FROM airdrops WHERE status = ?",
            ("joined",),
        ).fetchone()[0]
        replies = conn.execute(
            "SELECT COUNT(*) FROM telemetry"
        ).fetchone()[0]
        events = conn.execute(
            "SELECT COUNT(DISTINCT event) FROM telemetry"
        ).fetchone()[0]
    context = {"airdrops": joined, "replies": replies, "events": events}
    return await generate_persona_reply("log_stats_summary", context, session=session)


async def check_onboarding_message(
    user_id: int,
    text: str,
    username: str | None = None,
    session: aiohttp.ClientSession | None = None,
) -> str:
    """Return onboarding reply the first time a user sends a message."""
    if text.startswith("/"):
        return ""
    if user_id in _SEEN_USERS:
        return ""
    _SEEN_USERS.add(user_id)
    with SEEN_USERS_FILE.open("a") as fh:
        fh.write(f"{user_id}\n")
    context = {"user": username or user_id}
    return await generate_persona_reply("onboarding", context, session=session)
