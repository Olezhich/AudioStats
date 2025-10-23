from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .repositories import AlbumRepository
from .session import SessionFactory

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

        self.albums: AlbumRepository | None = None
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
