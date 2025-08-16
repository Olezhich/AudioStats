from audiostats.db.api import DBApi
from audiostats.handlers import TrackDTO
from tests import test_sessionmaker, test_engine

def test_upsert_albums(test_sessionmaker, processed_album_dtos):
    api = DBApi(test_sessionmaker)

    api.upsert_albums(processed_album_dtos)

    albums = api.get_all_albums()

    assert albums.sort(key=lambda x: x.title) == processed_album_dtos.sort(key=lambda x: x.title), 'Insert some albums to db'

    processed_album_dtos[0].tracks.pop(-1)
    processed_album_dtos[0].tracks.pop(2)
    processed_album_dtos[1].tracks.append(TrackDTO(title='New_Track_1', number=6, path='music/new_track_1.flac', offset=None, duration=None))
    processed_album_dtos[1].year = None

    api.upsert_albums(processed_album_dtos)

    albums=api.get_all_albums()

    assert albums.sort(key=lambda x: x.title) == processed_album_dtos.sort(key=lambda x: x.title), 'Update some albums in db'






