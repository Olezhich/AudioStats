import asyncio
import logging

import pytest
#from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from audiostats.db.models import Base

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для тестов"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_engine():
    """Создает асинхронный engine для тестов"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    return engine

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    async def setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())

    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

@pytest.fixture(scope="session", autouse=True)
def cleanup(test_engine):
    yield
    async def dispose():
        await test_engine.dispose()
    asyncio.run(dispose())