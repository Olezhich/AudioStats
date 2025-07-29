from dataclasses import dataclass


@dataclass(slots=True)
class TrackDTO:
    title : str
    number : int | None
    path : str
    offset : float | None
    duration : float | None

@dataclass(slots=True)
class AlbumDTO:
    title : str
    performer : str | None
    year : int | None
    path : str | None
    cover : str | None
    tracks : list[TrackDTO]

    
