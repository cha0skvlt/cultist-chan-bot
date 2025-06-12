"""Async PostgreSQL pool manager."""

from __future__ import annotations

import asyncpg

from .config import Settings

_POOL: asyncpg.Pool | None = None


async def create_pool(settings: Settings) -> asyncpg.Pool:
    """Initialize connection pool if needed."""
    global _POOL
    if _POOL is None:
        _POOL = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASS,
            database=settings.POSTGRES_NAME,
        )
    return _POOL


def get_pool() -> asyncpg.Pool:
    """Return initialized pool."""
    if _POOL is None:
        raise RuntimeError("Pool not initialized")
    return _POOL


async def close_pool() -> None:
    """Close pool and reset state."""
    global _POOL
    if _POOL is not None:
        await _POOL.close()
        _POOL = None
