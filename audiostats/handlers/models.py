from collections import Counter
from dataclasses import dataclass, field

from audiostats.domain.enums import Status, Success

@dataclass(slots=True, frozen=True)
class StatusDTO:
    status : Status
    success : Success

    def __repr__(self):
        return f'<StatusDTO(status={self.status}, success={self.success})>'

@dataclass(slots=True, frozen=True)
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
    statuses : list[StatusDTO] = field(default_factory=list)

    def __repr__(self):
        return f'''\n<AlbumDTO(title={self.title}, performer={self.performer}, year={self.year}, path={self.path}, cover={self.cover},
{'\n'.join(['\t' + repr(i) for i in self.tracks])}
{'\n'.join(['\t' + repr(i) for i in self.statuses])}
)>'''

    def __eq__(self, other):
        if not isinstance(other, AlbumDTO):
            return False
        return (
                self.title == other.title
                and self.performer == other.performer
                and self.year == other.year
                and self.path == other.path
                and self.cover == other.cover
                and Counter(self.tracks) == Counter(other.tracks)
                and Counter(self.statuses) == Counter(other.statuses)
        )

    
