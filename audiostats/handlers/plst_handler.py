import cuetools
import os
import subprocess

from typing import Any
from collections.abc import Iterator
from cuetools import TrackData
from .models import AlbumDTO, TrackDTO

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    librosa = None
    LIBROSA_AVAILABLE = False

MIN_TRACK_DURATION = 10 #Used to decide whether there are more tracks in the file or whether a new file should be started

def frame_t_sec(str_time : str) -> float:
    mm, ss, ff = map(float, str.split(':'))
    return mm * 60 + ss + ff / 75  # 1 frame = 1/75 sec

class PlayListHandler:
    """Class that processes the playlist, prepares the necessary data for each album for loading into the database"""
    def __init__(self, cfg : dict[str, Any]) -> None:
        self._config = cfg

    def process_playlist_paths(self, playlist : list[str]) -> Iterator[AlbumDTO]:
        """Processes the playlist line by line and provides the **AlbumDTO** objects for loading into db"""
        for path in playlist:
            if path.endswith('.cue'):
                album = self._process_cue(path)
                yield album
            else:
                pass

    def _process_cue(self, path: str) -> AlbumDTO:
        """AlbumDTO class constructor from cue sheet data"""
        with open(path, 'r') as f:
            cue = cuetools.load(f)
            current_dir = os.path.dirname(path)
            album = AlbumDTO(title=cue.title,
                             performer=cue.performer,
                             year=int(cue.rem.date),
                             path=path,
                             cover=self._get_cover_path(current_dir),
                             tracks=[i for i in self._process_cue_tracks(cue, current_dir)])
            return album

    def _get_cover_path(self, current_dir: str) -> str | None:
        """returns album cover filepath"""
        for file in os.listdir(current_dir):
            if any(file.lower() == i + j for i in self._config['CoverNames'] for j in self._config['CoverExtensions']):
                return os.path.join(current_dir, file)
        return None

    def _process_cue_tracks(self, cue : cuetools.AlbumData, current_dir : str) -> Iterator[TrackDTO]:
        next_offset = 0
        for track_cue in sorted(cue.tracks, reverse=True, key=lambda x: int(x.track)):
            offset, duration = self._get_offset_duration(track_cue, next_offset) if LIBROSA_AVAILABLE else None
            track = TrackDTO(title=track_cue.title,
                             number=int(track_cue.track),
                             path=os.path.join(current_dir, track_cue.link),
                             offset=offset,
                             duration=duration)
            yield track

    def _get_offset_duration(self, track_cue : TrackData, next_offset : float | None) -> tuple[float, float]:
        offset = frame_t_sec(track_cue.index['01']) if track_cue.index['01'] else 0
        duration = next_offset - offset if next_offset >= MIN_TRACK_DURATION else self._get_audiofile_duration(track_cue.link)
        return offset, duration

    def _get_audiofile_duration(self, path_to_file: str) -> float:
        if path_to_file.endswith('.ape'):
            return self._get_ape_duration(path_to_file)
        else:
            return librosa.get_duration(path=path_to_file)

    def _get_ape_duration(self, path_to_file: str) -> float:
        result = subprocess.run(
            [arg.replace('{path_to_file}', path_to_file) for arg in self._config['ApeDurationCmd']],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
