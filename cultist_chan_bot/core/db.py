"""Async database helpers using asyncpg."""

from __future__ import annotations

import json
from time import time

import asyncpg

from .config import Settings, load_config
from .database import create_pool, get_pool

_CFG = load_config()


async def migrate_pg(settings: Settings | None = None) -> None:
    """Create tables if they don't exist."""
    settings = settings or _CFG
    pool = await create_pool(settings)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airdrop_events (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                drop_name TEXT,
                timestamp DOUBLE PRECISION,
                status TEXT
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nft_events (
                id SERIAL PRIMARY KEY,
                nft_name TEXT,
                user_id BIGINT,
                timestamp DOUBLE PRECISION,
                action TEXT
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT,
                joined_at DOUBLE PRECISION
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airdrops (
                name TEXT,
                metadata TEXT,
                status TEXT,
                joined_at DOUBLE PRECISION
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                event TEXT,
                payload TEXT,
                response TEXT,
                timestamp DOUBLE PRECISION
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS nft_purchases (
                metadata TEXT,
                status TEXT,
                timestamp DOUBLE PRECISION
            )
            """
        )


async def get_airdrop_history() -> list[tuple[str, str, float]]:
    """Return recorded airdrops sorted by time."""
    try:
        pool = get_pool()
    except RuntimeError:
        return
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT name, status, joined_at FROM airdrops ORDER BY joined_at DESC"
        )
    return [(r["name"], r["status"], r["joined_at"]) for r in rows]


async def log_airdrop(drop: dict, status: str) -> None:
    """Insert airdrop participation result."""
    try:
        pool = get_pool()
    except RuntimeError:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO airdrops (name, metadata, status, joined_at) VALUES ($1, $2, $3, $4)",
            drop.get("name"),
            json.dumps(drop),
            status,
            time(),
        )


async def log_telemetry(event: str, payload: dict, response: str) -> None:
    """Record persona interaction."""
    try:
        pool = get_pool()
    except RuntimeError:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO telemetry (event, payload, response, timestamp) VALUES ($1, $2, $3, $4)",
            event,
            json.dumps(payload),
            response,
            time(),
        )


async def log_nft_purchase(nft: dict, status: str, timestamp: float) -> None:
    """Record NFT purchase action."""
    try:
        pool = get_pool()
    except RuntimeError:
        return []
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO nft_purchases (metadata, status, timestamp) VALUES ($1, $2, $3)",
            json.dumps(nft),
            status,
            timestamp,
        )

