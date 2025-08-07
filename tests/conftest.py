import cuetools
import pytest
import tomlcfg
import logging

from cuetools import TrackData

from audiostats.handlers import PlayListHandler,AlbumDTO, TrackDTO
from audiostats.handlers.plst_handler import LIBROSA_AVAILABLE


@pytest.fixture
def plst_handler_instance():
    class PlstHandlerApp(tomlcfg.BaseModel):
        def __init__(self):
            super().__init__('./config/config.toml')
            self.plst_handler = PlayListHandler(self._config['PlayList'])
    app = PlstHandlerApp()
    return app.plst_handler

@pytest.fixture(autouse=True, scope="session")
def setup_test_logging():
    """Basic test logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(name)s:%(message)s'
    )

@pytest.fixture
def playlist():
    return ['/music/Album1/Album1.cue', '/music/Track1.flac', '/music/Album2/Album2.cue', '/music/Album3/Album3.cue']

@pytest.fixture()
def mock_files(monkeypatch):
    def mock_open(filename, *args, **kwargs):
        class MockFile:
            def __enter__(self):
                return self
            def __exit__(self, *args, **kwargs):
                pass
            def read(self):
                if filename == '/music/Album1/Album1.cue':
                    return ''
                if filename == '/music/Album2/Album2.cue':
                    tracks = [TrackData(index={f'01' : f'00:{i//2}{i%2*5}:00'}, track=f'0{i+1}', title=f'Track 0{i+1}', link='Album.flac') for i in range(5)]
                    cue_sheet = cuetools.AlbumData(performer='The Performer',title='The Title Of Album', rem=cuetools.RemData(genre='Rock', date='1969'), tracks=tracks)
                    return cuetools.dumps(cue_sheet)
                else:
                    raise FileNotFoundError()

            def __iter__(self):
                return iter(self.read().splitlines())

            def readline(self):
                lines = self.read().splitlines()
                for line in lines:
                    yield line + '\n'
        return MockFile()
    monkeypatch.setattr('builtins.open', mock_open)

@pytest.fixture
def mock_listdir(monkeypatch):
    def mock_os_listdir(path):
        responses = {
            '/music/Album1': ['Cover.png'],
            '/music/Album2': ['Front.jpg'],
        }
        if path in responses:
            return responses[path]
        raise FileNotFoundError()
    monkeypatch.setattr('os.listdir', mock_os_listdir)

@pytest.fixture(autouse=True, scope="function")
def mock_get_duration(monkeypatch):
    DURATION_MAP = {
        "test.wav": 120.0,
        "long.ape": 180.0,
        "short.mp3": 60.0,
    }

    def mock_duration(self, path_to_file: str) -> float:
        return DURATION_MAP.get(path_to_file, 25.0)

    from audiostats.handlers import PlayListHandler
    monkeypatch.setattr(PlayListHandler, '_get_audiofile_duration', mock_duration)

@pytest.fixture()
def processed_album_dtos():
    album_list = []
    if LIBROSA_AVAILABLE:
        album2 = AlbumDTO(title='The Title Of Album', performer='The Performer', year=1969, path='/music/Album2/Album2.cue', cover='/music/Album2/Front.jpg',
                      tracks=[TrackDTO(f'Track 0{i+1}', number=i+1, path='/music/Album2/Album.flac', offset=i*5.0, duration=5.0) for i in range(4,-1,-1)])
    else:
        album2 = AlbumDTO(title='The Title Of Album', performer='The Performer', year=1969,
                          path='/music/Album2/Album2.cue', cover='/music/Album2/Front.jpg',
                          tracks=[
                              TrackDTO(f'Track 0{i + 1}', number=i + 1, path='/music/Album2/Album.flac', offset=None,
                                       duration=None) for i in range(4, -1, -1)])
    album_list.append(album2)
    return album_list