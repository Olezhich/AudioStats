import pytest

from audiostats.db.api import DBApi
from audiostats.handlers import TrackDTO
from tests import test_session_factory, test_engine#, setup_database

@pytest.mark.asyncio
async def test_upsert_albums(test_session_factory, processed_album_dtos):
    api = DBApi(test_session_factory)

    await api.upsert_albums(processed_album_dtos)

    albums = await api.get_all_albums()

    assert albums.sort(key=lambda x: x.title) == processed_album_dtos.sort(key=lambda x: x.title), 'Insert some albums to db'

    processed_album_dtos[0].tracks.pop(-1)
    processed_album_dtos[0].tracks.pop(2)
    processed_album_dtos[1].tracks.append(TrackDTO(title='New_Track_1', number=6, path='music/new_track_1.flac', offset=None, duration=None))
    processed_album_dtos[1].year = None

    await api.upsert_albums(processed_album_dtos)

    albums = await api.get_all_albums()

    assert albums.sort(key=lambda x: x.title) == processed_album_dtos.sort(key=lambda x: x.title), 'Update some albums in db'






