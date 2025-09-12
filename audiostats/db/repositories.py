import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Album
from audiostats.handlers import AlbumDTO

from audiostats.application.dto_mappers import create_album_dto_f_orm, update_album_orm_meta_f_dto, update_track_orm_f_dto, create_track_orm_f_dto


logger = logging.getLogger(__name__)

class AlbumRepository:
    def __init__(self, session : AsyncSession):
        self._session = session

    async def upsert(self, album_data : AlbumDTO):
        album = await self.find_by_title_performer(album_data.title, album_data.performer)

        if not album:
            album = Album()
            self._session.add(album)
        update_album_orm_meta_f_dto(album, album_data)

        old_tracks_by_title = {track.title: track for track in album.tracks}
        for dto in album_data.tracks:
            if dto.title in old_tracks_by_title:
                old_track = old_tracks_by_title.pop(dto.title)
                update_track_orm_f_dto(old_track, dto)
            else:
                track = create_track_orm_f_dto(dto)
                track.album = album
                album.tracks.append(track)

        for track in old_tracks_by_title.values():
            await self._session.delete(track)

        logger.info(f'Album upserted: {album_data}')

    async def find_by_title_performer(self, title : str, performer : str | None) -> Album | None:
        result = await self._session.execute(
            select(Album).where(
            Album.title == title, Album.performer == performer).options(
                selectinload(Album.tracks)
    ))
        return result.scalar_one_or_none()

    async def all(self) -> list[Album]:
        result = await self._session.scalars(select(Album).options(
        selectinload(Album.tracks)
    ))
        return [create_album_dto_f_orm(album) for album in result.all()]
