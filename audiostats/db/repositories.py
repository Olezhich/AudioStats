from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Album
from audiostats.handlers import AlbumDTO

from audiostats.application.dto_mappers import create_album_dto_f_orm, update_album_orm_meta_f_dto, update_track_orm_f_dto, create_track_orm_f_dto


class AlbumRepository:
    def __init__(self, session : Session):
        self._session = session

    def upsert(self, album_data : AlbumDTO):
        album = self.find_by_title_performer(album_data.title, album_data.performer)

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
                album.tracks.append(track)

        for track in old_tracks_by_title.values():
            album.tracks.remove(track)

    def find_by_title_performer(self, title : str, performer : str | None) -> Album | None:
        return self._session.query(Album).filter(Album.title == title and Album.performer == performer if performer else Album.performer.is_(None)).first()

    def all(self) -> list[Album]:
        return [create_album_dto_f_orm(album) for album in self._session.scalars(select(Album)).all()]
