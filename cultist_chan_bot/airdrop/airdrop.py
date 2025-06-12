"""Airdrop history storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from .logger import get_logger

DB_PATH = Path(__file__).with_name("bot.db")


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airdrop_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                status TEXT,
                joined_at REAL
            )
            """
        )


init_db()


def save_airdrop_history(name: str, status: str, timestamp: float) -> None:
    """Persist airdrop result."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO airdrop_log (name, status, joined_at) VALUES (?, ?, ?)",
            (name, status, timestamp),
        )
    get_logger(__name__).info("Saved airdrop %s with status %s", name, status)


def get_airdrop_history() -> list[tuple[str, str, float]]:
    """Return recorded airdrops sorted by timestamp desc."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT name, status, joined_at FROM airdrop_log ORDER BY joined_at DESC"
        ).fetchall()
    return rows
