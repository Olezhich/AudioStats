from sqlalchemy import String, Integer, UniqueConstraint, ForeignKey, Float
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()

MAX_PATH_FIELD_LEN = 200
MAX_STR_FIELD_LEN = 50

class Album(Base):
    """Album model"""
    __tablename__ = 'albums'

    __table_args__ = (
        UniqueConstraint('performer', 'title', name='uq_album_performer_title'),
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True) #album id
    title : Mapped[str] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=False) #album title
    performer : Mapped[str | None] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=True) #album performer
    year : Mapped[int | None] = mapped_column(Integer, nullable=True) #album release year
    path : Mapped[str | None] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True) #path to cue file if it exists
    cover : Mapped[str | None] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True) #path to album cover
    tracks : Mapped[list['Track']] = relationship('Track', back_populates='album')

    def __repr__(self):
        return f'<Album(year={self.year}, performer={self.performer}, title={self.title})>'

    def __str__(self):
        return f'{self.year} - {self.performer} - {self.title}'

class Track(Base):
    """Track model"""
    __tablename__ = 'tracks'

    id : Mapped[int] = mapped_column(Integer, primary_key=True) #track id
    title : Mapped[str] = mapped_column(String(MAX_STR_FIELD_LEN), nullable=False) #track title
    album_id : Mapped[int] = mapped_column(Integer, ForeignKey('albums.id', ondelete='CASCADE'), index=True) #album id
    number : Mapped[int | None] = mapped_column(Integer, nullable=True) #track number in album
    path : Mapped[str] = mapped_column(String(MAX_PATH_FIELD_LEN), nullable=True) #path to flac file with track
    offset : Mapped[float | None] = mapped_column(Float, nullable=True) #offset from the beginning of the file to the beginning of the track
    duration : Mapped[float | None] = mapped_column(Float, nullable=True) #track duration
    album : Mapped["Album"]= relationship('Album', back_populates='tracks')

    def __repr__(self):
        return f'<Track(title={self.title}, album_id={self.album_id}, number={self.number})>'

    def __str__(self):
        return f'{self.number} - {self.title}'