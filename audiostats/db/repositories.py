import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from audiostats.domain.enums import Status, Success
from .models import Album, AlbumStatus
from audiostats.handlers.models import AlbumDTO

from audiostats.application.dto_mappers import (
    create_album_dto_f_orm,
    update_album_orm_meta_f_dto,
    update_track_orm_f_dto,
    create_track_orm_f_dto,
    diff_track,
    diff_album_meta,
)


logger = logging.getLogger(__name__)


class AlbumRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, album_data: AlbumDTO):
        album = await self.find_by_title_performer(
            album_data.title, album_data.performer
        )
        album_status = None

        if not album:  # if new album
            album = Album()
            album_status = Status.ADDED
            self._session.add(album)
        elif diff_album_meta(album, album_data):  # if album meta modified
            album_status = Status.MODIFIED

        update_album_orm_meta_f_dto(album, album_data)

        old_tracks_by_title = {track.title: track for track in album.tracks}
        for dto in album_data.tracks:
            if dto.title in old_tracks_by_title:
                old_track = old_tracks_by_title.pop(dto.title)
                if diff_track(old_track, dto):
                    album_status = Status.MODIFIED
                update_track_orm_f_dto(old_track, dto)
            else:
                if not album_status:
                    album_status = Status.MODIFIED
                track = create_track_orm_f_dto(dto)
                track.album = album
                album.tracks.append(track)

        for track in old_tracks_by_title.values():
            album_status = Status.MODIFIED
            await self._session.delete(track)

        if album_status:
            status = AlbumStatus(
                album=album, status=album_status, success=Success.SUCCESS
            )
            self._session.add(status)

        logger.info(f'Album upserted: {album_data}')

    async def find_by_title_performer(
        self, title: str, performer: str | None
    ) -> Album | None:
        result = await self._session.execute(
            select(Album)
            .where(Album.title == title, Album.performer == performer)
            .options(selectinload(Album.tracks))
        )
        return result.scalar_one_or_none()

    async def all(self) -> list[Album]:
        result = await self._session.scalars(
            select(Album).options(selectinload(Album.tracks))
        )
        return [create_album_dto_f_orm(album) for album in result.all()]

    async def all_w_status(self) -> list[Album]:
        result = await self._session.scalars(
            select(Album)
            .options(selectinload(Album.tracks))
            .options(selectinload(Album.album_statuses))
        )
        return [create_album_dto_f_orm(album) for album in result.all()]
