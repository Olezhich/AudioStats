import asyncio
import logging
from collections.abc import Iterator

from .uow import UnitOfWork

from audiostats.handlers import AlbumDTO
from audiostats.db.session import SessionFactory


logger = logging.getLogger(__name__)

class DBApi:
    def __init__(self, db_url : str):
        self._session_factory = SessionFactory(db_url)

    async def _upsert_album(self, album : AlbumDTO):
        async with self._session_factory as sf:
            async with UnitOfWork(sf()) as uow:
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
        async with self._session_factory as sf:
            async with UnitOfWork(sf()) as uow:
                return await uow.albums.all()

