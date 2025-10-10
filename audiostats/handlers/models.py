from dataclasses import dataclass, field
from datetime import datetime

from audiostats.domain import Status, Success

@dataclass(slots=True)
class StatusDTO:
    status : Status
    success : Success
    # timestamp : datetime | None = field(default=None, compare=False)

    # def __eq__(self, other):
    #     if not isinstance(other, StatusDTO):
    #         return NotImplemented
    #     return self.status == other.status and self.success == other.success

    def __repr__(self):
        return f'<StatusDTO(status={self.status}, success={self.success})>'

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
    statuses : list[StatusDTO] = field(default_factory=list)

    def __repr__(self):
        return f'''\n<AlbumDTO(title={self.title}, performer={self.performer}, year={self.year}, path={self.path}, cover={self.cover},
{'\n'.join(['\t' + repr(i) for i in self.tracks])}
{'\n'.join(['\t' + repr(i) for i in self.statuses])}
)>'''

    
