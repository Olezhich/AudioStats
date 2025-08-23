from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
#from sqlalchemy.orm import sessionmaker, Session
import logging

from .repositories import AlbumRepository

logger = logging.getLogger(__name__)

class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session : AsyncSession | None = None
        self.albums : AlbumRepository | None = None
        logger.debug(f'UoF initialized: {self}')

    async def __aenter__(self):
        self._session = self._session_factory()
        self.albums = AlbumRepository(self._session)
        logger.debug(f'AlbumRepo initialised: {self.albums}, Current Session: {self._session}')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()
        logger.debug(f'Session closed')

