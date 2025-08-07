from dataclasses import dataclass


@dataclass(slots=True)
class TrackDTO:
    title : str
    number : int | None
    path : str
    offset : float | None
    duration : float | None

    def __repr__(self):
        return f'''<TrackDTO(title={self.title}, number={self.number}, offset={self.offset}, duration={self.duration}, path={self.path})>'''

@dataclass(slots=True)
class AlbumDTO:
    title : str
    performer : str | None
    year : int | None
    path : str | None
    cover : str | None
    tracks : list[TrackDTO]

    def __repr__(self):
        return f'''\n<AlbumDTO(title={self.title}, performer={self.performer}, year={self.year}, path={self.path}, cover={self.cover},
{'\n'.join(['\t' + repr(i) for i in self.tracks])}
)>'''

    
