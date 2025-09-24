# import logging
#
# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
# from sqlalchemy.ext.asyncio import async_sessionmaker
#
# from testcontainers.postgres import PostgresContainer
#
# from audiostats.db.models import Base
#
# logger = logging.getLogger(__name__)
#
# POSTGRES_CONTAINER = None
# TEST_ENGINE = None
#
# @pytest.fixture(scope="session")
# def event_loop():
#     import asyncio
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()
#
# @pytest.fixture(scope="session")
# async def test_engine():
#     global POSTGRES_CONTAINER, TEST_ENGINE
#     POSTGRES_CONTAINER = PostgresContainer("postgres:15")
#     POSTGRES_CONTAINER.start()
#     DATABASE_URL = POSTGRES_CONTAINER.get_connection_url() \
#             .replace("postgresql://", "postgresql+asyncpg://")\
#             .replace("postgresql+psycopg2://", "postgresql+asyncpg://")
#     engine = create_async_engine(DATABASE_URL, echo=False)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     TEST_ENGINE = engine
#     return engine
#
# @pytest.fixture(scope="session")
# async def test_session_factory(test_engine):
#     engine = test_engine
#     return async_sessionmaker(bind=await engine, expire_on_commit=False)
#
# @pytest.fixture(scope="session", autouse=True)
# async def cleanup_test_resources():
#     yield
#     global TEST_ENGINE, POSTGRES_CONTAINER
#     if TEST_ENGINE:
#         await TEST_ENGINE.dispose()
#     if POSTGRES_CONTAINER:
#         POSTGRES_CONTAINER.stop()

