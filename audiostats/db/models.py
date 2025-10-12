from datetime import datetime

from sqlalchemy import String, Integer, UniqueConstraint, ForeignKey, Float, Enum, DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

from audiostats.domain import Status, Success

Base = declarative_base()

MAX_PATH_FIELD_LEN = 200
MAX_STR_FIELD_LEN = 50

class Album(Base):
    """Represents **albums** table line as orm object

    Pair ``performer`` - ``title`` should be **unique**

    :ivar id: Album id
    :ivar title: Album title
    :ivar performer: Album performer
    :ivar year: Album release year
    :ivar path: Path to ``.cue`` file
    :ivar cover: Path to album cover file (image)
    :ivar tracks: Collection of tracks contained in the album
    """

    __tablename__ = 'albums'

    __table_args__ = (
        UniqueConstraint('performer', 'title', name='uq_album_performer_title'),
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    title : Mapped[str] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=False)
    performer : Mapped[str | None] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=True)
    year : Mapped[int | None] = mapped_column(Integer, nullable=True)
    path : Mapped[str | None] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True)
    cover : Mapped[str | None] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True)
    tracks : Mapped[list['Track']] = relationship('Track', back_populates='album', lazy='noload')
    album_statuses : Mapped[list['AlbumStatus']] = relationship('AlbumStatus', back_populates='album', lazy='noload')

    def __repr__(self):
        return f'<Album(year={self.year}, performer={self.performer}, title={self.title})>'

    def __str__(self):
        return f'{self.year} - {self.performer} - {self.title}'

class Track(Base):
    """Represents **tracks** table line as orm object

    :ivar id: Track id
    :ivar title: Track title
    :ivar album_id: Album id
    :ivar number: Track number in album
    :ivar path: Path to ``.flac`` or another audiofile with track
    :ivar offset: Offset from the beginning of the file to the beginning of the track `(in seconds)`
    :ivar duration: Track duration `(in seconds)`
    :ivar album: Relationship to the parent album
    """
    __tablename__ = 'tracks'

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    title : Mapped[str] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=False)
    album_id : Mapped[int] = mapped_column(Integer, ForeignKey('albums.id', ondelete='CASCADE'), index=True)
    number : Mapped[int | None] = mapped_column(Integer, nullable=True)
    path : Mapped[str] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True)
    offset : Mapped[float | None] = mapped_column(Float, nullable=True)
    duration : Mapped[float | None] = mapped_column(Float, nullable=True)
    album : Mapped["Album"]= relationship('Album', back_populates='tracks', lazy='noload')

    def __repr__(self):
        return f'<Track(title={self.title}, album_id={self.album_id}, number={self.number})>'

    def __str__(self):
        return f'{self.number} - {self.title}'


class AlbumStatus(Base):
    """Represents **album_statuses** table line as orm object

    :ivar id: AlbumStatus id
    :ivar album_id: Album id
    :ivar time_stamp: timestamp when the entry was added
    :ivar status: insertion status, may be `added` or `modified`
    :ivar success: processing success, may be `success` or `warning` if there was a warning while process the album cue
    :ivar album: Relationship to the parent album
    """

    __tablename__ = 'album_statuses'

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id : Mapped[int] = mapped_column(Integer, ForeignKey('albums.id', ondelete='CASCADE'), index=True)
    time_stamp : Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), default=func.now())
    status : Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    success : Mapped[Success] = mapped_column(Enum(Success), nullable=False)
    album : Mapped["Album"] = relationship('Album', back_populates='album_statuses', lazy='noload')




