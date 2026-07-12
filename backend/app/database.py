# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

# Module-level singletons: engine's connection pool is created once per
# process and is not safe to split across per-test event loops (tests use a
# session-scoped asyncio event loop for this reason - see pytest.ini).
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped AsyncSession, closed
    automatically when the request finishes (via the async context manager)."""
    async with AsyncSessionLocal() as session:
        yield session
