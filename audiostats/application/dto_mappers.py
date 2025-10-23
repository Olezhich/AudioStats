from audiostats.db.models import Album, Track

from audiostats.handlers.models import AlbumDTO, TrackDTO, StatusDTO

def update_track_orm_f_dto(old : Track, new : TrackDTO) -> None:
    old.title = new.title
    old.number = new.number
    old.path = new.path
    old.offset = new.offset
    old.duration = new.duration

def create_track_orm_f_dto(track : TrackDTO) -> Track:
    created = Track()
    update_track_orm_f_dto(created, track)
    return created

def update_album_orm_meta_f_dto(old : Album, new : AlbumDTO):
    old.title = new.title
    old.performer = new.performer
    old.year = new.year
    old.path = new.path
    old.cover = new.cover

def create_album_dto_f_orm(album : Album):
    return AlbumDTO(title=album.title,
                    performer=album.performer,
                    year=album.year,
                    path=album.path,
                    cover=album.cover,
                    tracks=[TrackDTO(title=track.title,
                                     number=track.number,
                                     path=track.path,
                                     offset=track.offset,
                                     duration=track.duration) for track in album.tracks],
                    statuses=[StatusDTO(status=status.status,
                                        success=status.success) for status in album.album_statuses])

def diff_album_meta(old : Album, new : AlbumDTO) -> bool:
    return any([old.title != new.title,
            old.performer != new.performer,
            old.year != new.year,
            old.path != new.path,
            old.cover != new.cover])

def diff_track(old : Track, new : TrackDTO) -> bool:
    return any([old.title != new.title,
                old.number != new.number,
                old.path != new.path,
                old.offset != new.offset,
                old.duration != new.duration])