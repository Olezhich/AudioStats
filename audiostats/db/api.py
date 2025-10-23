import asyncio
import logging
from collections.abc import Iterator

from .uow import UnitOfWork

from audiostats.handlers.models import AlbumDTO
from audiostats.db.session import SessionFactory


logger = logging.getLogger(__name__)

class DBApi:
    def __init__(self, db_url : str, workers : int = 5, queue_sz : int = 10):
        self._session_factory = SessionFactory(db_url)
        self._queue: asyncio.Queue[AlbumDTO | None] = asyncio.Queue(maxsize=queue_sz)
        self._num_workers = workers

    async def _album_upserter(self):
        async with self._session_factory as sf:
            unit_of_work = UnitOfWork(sf)
            async with unit_of_work() as uow:
                while True:
                    album = await self._queue.get()
                    try:
                        if not album:
                            break
                        await uow.albums.upsert(album)
                    finally:
                        self._queue.task_done()

    async def upsert_albums(self, albums : Iterator[AlbumDTO]):
        workers = [asyncio.create_task(self._album_upserter()) for _ in range(self._num_workers)]

        for album in albums:
            await self._queue.put(album)

        await self._queue.join()

        for _ in range(self._num_workers):
            await self._queue.put(None)

        await asyncio.gather(*workers)

    async def get_all_albums(self):
        async with self._session_factory as sf:
            unit_of_work = UnitOfWork(sf)
            async with unit_of_work() as uow:
                return await uow.albums.all()

    async def get_all_albums_w_status(self):
        async with self._session_factory as sf:
            unit_of_work = UnitOfWork(sf)
            async with unit_of_work() as uow:
                return await uow.albums.all_w_status()

