import logging

from audiostats.db.api import DBApi
from tests import test_sessionmaker, test_engine

def test_upsert_albums(test_sessionmaker, processed_album_dtos):
    api = DBApi(test_sessionmaker)

    api.upsert_albums(processed_album_dtos)

    albums = api.get_all_albums()

    assert albums.sort(key=lambda x: x.title) == processed_album_dtos.sort(key=lambda x: x.title)





