"""Lazy PostgreSQL engine, session factory, and FastAPI dependency."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from threading import Lock

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_lock = Lock()


def get_engine() -> AsyncEngine:
    """Return the shared SQLAlchemy async engine, creating it lazily."""
    global _engine, _session_factory
    if _engine is None:
        with _lock:
            if _engine is None:
                settings = get_settings()
                _engine = create_async_engine(
                    settings.database_url,
                    echo=settings.debug,
                    pool_pre_ping=True,
                    pool_recycle=1800,
                )
                _session_factory = async_sessionmaker(
                    bind=_engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autoflush=False,
                    autocommit=False,
                )
    return _engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield one request-scoped PostgreSQL session and close it safely."""
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session


async def dispose_engine() -> None:
    """Dispose of the SQLAlchemy connection pool during application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
