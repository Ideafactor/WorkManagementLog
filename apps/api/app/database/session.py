"""Async database engine and request session dependencies."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Create the pooled runtime engine once per process."""
    return create_async_engine(
        str(get_settings().database_url_pooled),
        pool_pre_ping=True,
        connect_args={"timeout": 5, "command_timeout": 30},
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create sessions that retain values after commit."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_database() -> AsyncIterator[AsyncSession]:
    """Yield one request-owned database session."""
    async with get_session_factory()() as database:
        yield database
