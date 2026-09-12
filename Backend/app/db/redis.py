"""Lazy Redis client lifecycle and FastAPI dependency."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from redis.asyncio import Redis


_redis_client: "Redis | None" = None


def get_redis_client() -> "Redis":
    """Return the shared async Redis client, creating it lazily."""
    global _redis_client
    if _redis_client is None:
        from redis.asyncio import Redis

        _redis_client = Redis.from_url(
            get_settings().redis_url,
            encoding="utf-8",
            decode_responses=True,
            health_check_interval=30,
        )
    return _redis_client


async def get_redis() -> AsyncGenerator["Redis", None]:
    """Yield the shared Redis client for request-scoped dependencies."""
    yield get_redis_client()


async def close_redis() -> None:
    """Close the shared Redis client during application shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
