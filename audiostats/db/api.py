import asyncio
import logging
from collections.abc import Iterator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
#from sqlalchemy.orm import sessionmaker, Session
from .uof import UnitOfWork

from audiostats.handlers import AlbumDTO


logger = logging.getLogger(__name__)

class DBApi:
    def __init__(self, session_factory : async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def _upsert_album(self, album : AlbumDTO):
        async with UnitOfWork(self._session_factory) as uow:
            await uow.albums.upsert(album)

    async def upsert_albums(self, albums : Iterator[AlbumDTO]):
        batch = []
        for album in albums:
            batch.append(self._upsert_album(album))
            if len(batch) > 10:
                await asyncio.gather(*batch)
                batch.clear()
        if batch:
            await asyncio.gather(*batch)

    async def get_all_albums(self):
        async with UnitOfWork(self._session_factory) as uow:
            return await uow.albums.all()

