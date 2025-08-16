from sqlalchemy.orm import sessionmaker, Session
import logging

from .repositories import AlbumRepository

logger = logging.getLogger(__name__)

class UnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory
        self._session : Session | None = None
        self.albums : AlbumRepository | None = None
        logger.debug(f'UoF initialized: {self}')

    def __enter__(self):
        self._session = self._session_factory()
        self.albums = AlbumRepository(self._session)
        logger.debug(f'AlbumRepo initialised: {self.albums}, Current Session: {self._session}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._session.rollback()
        else:
            self._session.commit()
        self._session.close()
        logger.debug(f'Session closed')

