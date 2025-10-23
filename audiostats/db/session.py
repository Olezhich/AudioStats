from asyncio import Semaphore
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class SessionFactory:
    def __init__(self, db_url: str, max_sessions: int = 20):
        self._engine = create_async_engine(
            url=db_url, pool_size=max_sessions, max_overflow=0
        )
        self._session_maker = async_sessionmaker(bind=self._engine)
        self._semaphore = Semaphore(max_sessions)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        session = None
        try:
            await self._semaphore.acquire()
            session = self._session_maker()
            yield session
        except Exception:
            raise
        finally:
            if session:
                await session.close()
                self._semaphore.release()
