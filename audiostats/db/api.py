import logging
import time
from collections.abc import Iterator

from sqlalchemy.orm import sessionmaker, Session
from .uof import UnitOfWork

from audiostats.handlers import AlbumDTO


logger = logging.getLogger(__name__)

class DBApi:
    def __init__(self, session_factory : sessionmaker[Session]):
        self._session_factory = session_factory

    def upsert_albums(self, albums : Iterator[AlbumDTO]):
        t_start = time.time()
        with UnitOfWork(self._session_factory) as uof:
            total, success = 0, 0
            for album in albums:
                uof.albums.upsert(album)
                total += 1
                success += 1
            logger.info(f'Albums updated/inserted in {(time.time() - t_start) * 1000:.3f} ms. Total: {total}, success: {success}')

    def get_all_albums(self):
        t_start = time.time()
        with UnitOfWork(self._session_factory) as uof:
            return uof.albums.all()

