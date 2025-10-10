import os

import pytest
import dotenv
import logging
import copy

from audiostats.db.api import DBApi
from audiostats.handlers import TrackDTO, StatusDTO
from audiostats.domain import Status, Success

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_async_upsert_albums(processed_album_dtos):
    #db api initialisation
    dotenv.load_dotenv()
    db_url = os.getenv('ASYNC_DB_URL')

    api = DBApi(db_url)

    #Upserting base album set
    logger.info(f'incoming dtos: {processed_album_dtos}')

    await api.upsert_albums(processed_album_dtos)

    albums = await api.get_all_albums_w_status()

    logger.info(f'db state after first albums upsert: {albums}')

    target_album_dtos = copy.deepcopy(processed_album_dtos)
    for i in target_album_dtos:
        i.statuses.append(StatusDTO(status=Status.ADDED, success=Success.SUCCESS))

    assert sorted(albums, key=lambda x: x.title) == sorted(target_album_dtos,
        key=lambda x: x.title), 'Insert some albums to db'

    #Upserting muted album set
    muted_album_dtos = copy.deepcopy(processed_album_dtos)

    muted_album_dtos[0].tracks.pop(-1)
    muted_album_dtos[0].tracks.pop(2)
    muted_album_dtos[1].tracks.append(
        TrackDTO(title='New_Track_1', number=6, path='music/new_track_1.flac', offset=None, duration=None))
    muted_album_dtos[1].year = None

    logger.info(f'muted album dtos: {muted_album_dtos}')

    await api.upsert_albums(muted_album_dtos)

    albums = await api.get_all_albums_w_status()

    logger.info(f'db state after first albums update: {albums}')

    target_muted_album_dtos = copy.deepcopy(muted_album_dtos)
    for i in target_muted_album_dtos:
        i.statuses.append(StatusDTO(status=Status.ADDED, success=Success.SUCCESS))
    target_muted_album_dtos[0].statuses.append(StatusDTO(status=Status.MODIFIED, success=Success.SUCCESS))
    target_muted_album_dtos[1].statuses.append(StatusDTO(status=Status.MODIFIED, success=Success.SUCCESS))

    assert sorted(albums, key=lambda x: x.title) == sorted(target_muted_album_dtos,
        key=lambda x: x.title), 'Update some albums in db'

