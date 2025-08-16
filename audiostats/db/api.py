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
        with UnitOfWork(self._session_factory) as uof:
            total, success = 0, 0
            for album in albums:
                uof.albums.upsert(album)
                total += 1
                success += 1

    def get_all_albums(self):
        with UnitOfWork(self._session_factory) as uof:
            return uof.albums.all()

