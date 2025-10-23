import time
import cuetools
import os
import subprocess
import logging

from typing import Any
from collections.abc import Iterator
from cuetools import TrackData
from types import ModuleType

from .models import AlbumDTO, TrackDTO

librosa: ModuleType | None = None
LIBROSA_AVAILABLE = False

try:
    #import librosa
    import librosa as _librosa
    librosa = _librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    pass

MIN_TRACK_DURATION = 10 #Used to decide whether there are more tracks in the file or whether a new file should be started

logger = logging.getLogger(__name__)

def frame_t_sec(str_time : str) -> float:
    mm, ss, ff = map(float, str_time.split(':'))
    return mm * 60 + ss + ff / 75  # 1 frame = 1/75 sec

class PlayListHandler:
    """Class that processes the playlist, prepares the necessary data for each album for loading into the database"""
    def __init__(self, cfg : dict[str, Any]) -> None:
        self._config = cfg

    def process_playlist_paths(self, playlist : list[str]) -> Iterator[AlbumDTO]:
        """Processes the playlist line by line and provides the **AlbumDTO** objects for loading into db"""
        t_start = time.time()
        files_total = 0
        files_processed = 0
        for path in playlist:
            if path.endswith('.cue'):
                album = self._process_cue(path)
                if album:
                    files_processed += 1
                    yield album
            files_total += 1
        logger.info(f'Playlist processed in {(time.time()-t_start)*1000:.3f} ms. Files total: {files_total}, successfully processed: {files_processed}')

    def _process_cue(self, path: str) -> AlbumDTO | None:
        """AlbumDTO class constructor from cue sheet data"""
        try:
            logger.debug(f'Process cue file: {path}')
            with open(path, 'r') as f:
                cue = cuetools.load(f)
                current_dir = os.path.dirname(path)

                if not (title:=cue.title):
                    logger.warning(f'No title in album: path={path}')
                    return None

                year = None
                if cue.rem.date:
                    try:
                        year = int(cue.rem.date)
                    except ValueError:
                        logger.warning(f'No correct date in album: {cue.performer} - {cue.title} - {path}')
                else:
                    logger.warning(f'No any date in album: {cue.performer} - {cue.title} - {path}')

                album = AlbumDTO(title=title,
                                 performer=cue.performer,
                                 year=year,
                                 path=path,
                                 cover=self._get_cover_path(current_dir),
                                 tracks=[i for i in self._process_cue_tracks(cue, current_dir)])

                if len(album.tracks) < 1:
                    logger.warning(f'No tracks in album: {cue.performer} - {cue.title} - {path}')
                    return None
                logger.debug(f'\nSuccessfully processed: {album}')
                return album
        except FileNotFoundError:
            logger.warning(f'No such file: {path}')
            return None
        except UnicodeDecodeError:
            logger.warning(f'Cant read file: {path}')
            return None


    def _get_cover_path(self, current_dir: str) -> str | None:
        """returns album cover filepath"""
        for file in os.listdir(current_dir):
            if any(file.lower() == i + j for i in self._config['CoverNames'] for j in self._config['CoverExtensions']):
                return os.path.join(current_dir, file)
        return None

    def _process_cue_tracks(self, cue : cuetools.AlbumData, current_dir : str) -> Iterator[TrackDTO]:
        offset: float = 0
        duration: float
        for track_cue in sorted(cue.tracks, reverse=True, key=lambda x: int(x.track)):
            offset, duration = self._get_offset_duration(current_dir, track_cue, offset) if LIBROSA_AVAILABLE else (0.0,0.0)
            if not (title:=track_cue.title):
                logger.warning(f'No title in track: {track_cue.track}]')
            else:
                track = TrackDTO(title=title,
                             number=int(track_cue.track),
                             path=os.path.join(current_dir, track_cue.link),
                             offset=offset if LIBROSA_AVAILABLE else None,
                             duration=duration if LIBROSA_AVAILABLE else None)
                yield track

    def _get_offset_duration(self, current_dir : str, track_cue : TrackData, next_offset : float | None) -> tuple[float, float]:
        offset = frame_t_sec(track_cue.index['01']) if track_cue.index['01'] else 0
        duration = next_offset - offset if next_offset is not None and next_offset >= MIN_TRACK_DURATION else self._get_audiofile_duration(os.path.join(current_dir,track_cue.link)) - offset
        return offset, duration

    def _get_audiofile_duration(self, path_to_file: str) -> float:
        if path_to_file.endswith('.ape'):
            return self._get_ape_duration(path_to_file)
        else:
            if librosa is not None:
                return librosa.get_duration(path=path_to_file)
            raise RuntimeError('librosa is unavailable')

    def _get_ape_duration(self, path_to_file: str) -> float:
        result = subprocess.run(
            [arg.replace('{path_to_file}', path_to_file) for arg in self._config['ApeDurationCmd']],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
