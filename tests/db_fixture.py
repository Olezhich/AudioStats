import asyncio
import logging

import pytest
#from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from audiostats.db.models import Base

logger = logging.getLogger(__name__)

# @pytest.fixture(scope="session")
# def test_engine():
#     engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
#     Base.metadata.create_all(engine)
#     yield engine
#     engine.dispose()

# @pytest.fixture(scope="session")
# def test_sessionmaker(test_engine):
#     sessionfactory = sessionmaker(bind=test_engine)
#     logger.debug(f'session type: {type(sessionfactory)}')
#     return sessionfactory

# @pytest.fixture(scope="function")
# def event_loop():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     yield loop
#     loop.close()
#
# @pytest.fixture(scope='function')
# async def test_engine():
#     engine: AsyncEngine = create_async_engine(
#         "sqlite+aiosqlite:///:memory:",
#         connect_args={"check_same_thread": False},
#         echo=False,
#     )
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield engine
#     await engine.dispose()
#
# @pytest.fixture(scope='function')
# async def test_sessionmaker(test_engine):
#     factory = async_sessionmaker(
#         bind=test_engine,
#         class_=AsyncSession,
#         expire_on_commit=False,
#         autoflush=False,
#         future=True,
#     )
#     print("Type of test_engine:",
#           type(test_engine))  # ← Должно быть: <class 'sqlalchemy.ext.asyncio.engine.AsyncEngine'>
#     print("test_engine:", test_engine)
#     return factory

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
    yield engine
    engine.sync_engine.dispose()

# @pytest.fixture(scope="session", autouse=True)
# async def setup_database(test_engine):
#     """Создание и удаление таблиц"""
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Создает async_sessionmaker который ожидает UnitOfWork"""

    async def setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Запускаем setup
    import asyncio
    asyncio.run(setup())

    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )