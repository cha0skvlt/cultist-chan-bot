"""Database interactions."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from time import time

from .config import load_config

_CFG = load_config()
DB_PATH = Path(_CFG.DB_PATH)


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db(db_path: str | None = None) -> None:
    """Initialize database and create tables if they don't exist."""
    global DB_PATH
    DB_PATH = Path(db_path or _CFG.DB_PATH)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airdrop_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                drop_name TEXT,
                timestamp REAL,
                status TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nft_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nft_name TEXT,
                user_id INTEGER,
                timestamp REAL,
                action TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                joined_at REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airdrops (
                name TEXT,
                metadata TEXT,
                status TEXT,
                joined_at REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                event TEXT,
                payload TEXT,
                response TEXT,
                timestamp REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nft_purchases (
                metadata TEXT,
                status TEXT,
                timestamp REAL
            )
            """
        )


def get_airdrop_history() -> list[tuple[str, str, float]]:
    """Return recorded airdrops sorted by time."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT name, status, joined_at FROM airdrops ORDER BY joined_at DESC"
        ).fetchall()
    return rows


def log_airdrop(drop: dict, status: str) -> None:
    """Insert airdrop participation result."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO airdrops (name, metadata, status, joined_at) VALUES (?, ?, ?, ?)",
            (drop.get("name"), json.dumps(drop), status, time()),
        )


def log_telemetry(event: str, payload: dict, response: str) -> None:
    """Record persona interaction."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO telemetry (event, payload, response, timestamp) VALUES (?, ?, ?, ?)",
            (event, json.dumps(payload), response, time()),
        )


def log_nft_purchase(nft: dict, status: str, timestamp: float) -> None:
    """Record NFT purchase action."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO nft_purchases (metadata, status, timestamp) VALUES (?, ?, ?)",
            (json.dumps(nft), status, timestamp),
        )

