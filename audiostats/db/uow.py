from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import logging

from .repositories import AlbumRepository
from .session import SessionFactory

logger = logging.getLogger(__name__)

class UnitOfWork:
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory
        self._session : AsyncSession | None = None

        self.albums : AlbumRepository | None = None
        logger.debug(f'UoF initialized: {self}')

    @asynccontextmanager
    async def __call__(self):
        async with self._session_factory.get_session() as session:
            self._session = session
            self.albums = AlbumRepository(self._session)
            try:
                yield self
                await self._session.commit()
            except Exception:
                await self._session.rollback()
                raise

    # async def __aenter__(self):
    #     async with self._session_factory as sf:
    #         await self._session = sf.get_session()
    #     self.albums = AlbumRepository(self._session)
    #     logger.debug(f'AlbumRepo initialised: {self.albums}, Current Session: {self._session}')
    #     return self
    #
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     if exc_type is not None:
    #         await self._session.rollback()
    #     else:
    #         await self._session.commit()
    #     await self._session.close()
    #     logger.debug(f'Session closed')

