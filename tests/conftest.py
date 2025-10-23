import cuetools
import pytest
import tomlcfg
import logging

from cuetools import TrackData

from audiostats.handlers.plst_handler import PlayListHandler, LIBROSA_AVAILABLE
from audiostats.handlers.models import AlbumDTO, TrackDTO, StatusDTO
from audiostats.domain.enums import Status, Success


@pytest.fixture
def plst_handler_instance():
    class PlstHandlerApp(tomlcfg.BaseModel):
        def __init__(self):
            super().__init__('./config/config.toml')
            self.plst_handler = PlayListHandler(self._config['PlayList'])

    app = PlstHandlerApp()
    return app.plst_handler


@pytest.fixture(autouse=True, scope='session')
def setup_test_logging():
    """Basic test logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s'
    )


@pytest.fixture
def playlist():
    return [
        '/music/Album1/Album1.cue',
        '/music/Track1.flac',
        '/music/Album2/Album2.cue',
        '/music/Album3/Album3.cue',
        '/music/Album4/Album4.cue',
    ]


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
                    tracks = [
                        TrackData(
                            index={'01': f'{i // 2}{(i % 2) * 5}:00:00'},
                            track=f'0{i + 1}',
                            title=f'Track 0{i + 1}',
                            link='Album.flac',
                        )
                        for i in range(5)
                    ]
                    cue_sheet = cuetools.AlbumData(
                        performer='The Performer',
                        title='The Title Of Album2',
                        rem=cuetools.RemData(genre='Rock', date='1969'),
                        tracks=tracks,
                    )
                    return cuetools.dumps(cue_sheet)
                if filename == '/music/Album3/Album3.cue':
                    tracks = [
                        TrackData(
                            index={'01': '00:00:00'},
                            track=f'0{i + 1}',
                            title=f'Track 0{i + 1}',
                            link=f'Track0{i + 1}.flac',
                        )
                        for i in range(5)
                    ]
                    cue_sheet = cuetools.AlbumData(
                        performer='The Performer',
                        title='The Title Of Album3',
                        rem=cuetools.RemData(genre='Rock', date='1969'),
                        tracks=tracks,
                    )
                    return cuetools.dumps(cue_sheet)
                if filename == '/music/Album4/Album4.cue':
                    tracks = [
                        TrackData(
                            index={'01': f'{(i % 3) // 2}{((i % 3) % 2) * 5}:00:00'},
                            track=f'0{i + 1}',
                            title=f'Track 0{i + 1}',
                            link=f'Side{"A" if i < 3 else "B"}.flac',
                        )
                        for i in range(6)
                    ]
                    cue_sheet = cuetools.AlbumData(
                        performer='The Performer',
                        title='The Title Of Album4',
                        rem=cuetools.RemData(genre='Rock', date='1970'),
                        tracks=tracks,
                    )
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
            '/music/Album3': ['Front.png'],
            '/music/Album4': ['Cover.jpg'],
        }
        if path in responses:
            return responses[path]
        raise FileNotFoundError()

    monkeypatch.setattr('os.listdir', mock_os_listdir)


@pytest.fixture(autouse=True, scope='function')
def mock_get_duration(monkeypatch):
    duration_map = {
        '/music/Album2/Album.flac': 25.0 * 60,
        '/music/Album3/Track01.flac': 5.0 * 60,
        '/music/Album3/Track02.flac': 5.0 * 60,
        '/music/Album3/Track03.flac': 5.0 * 60,
        '/music/Album3/Track04.flac': 5.0 * 60,
        '/music/Album3/Track05.flac': 5.0 * 60,
        '/music/Album4/SideA.flac': 15.0 * 60,
        '/music/Album4/SideB.flac': 15.0 * 60,
    }

    def mock_duration(self, path_to_file: str) -> float:
        return duration_map.get(path_to_file)

    from audiostats.handlers.plst_handler import PlayListHandler

    monkeypatch.setattr(PlayListHandler, '_get_audiofile_duration', mock_duration)


@pytest.fixture()
def processed_album_dtos():
    album_list = []
    album2 = AlbumDTO(
        title='The Title Of Album2',
        performer='The Performer',
        year=1969,
        path='/music/Album2/Album2.cue',
        cover='/music/Album2/Front.jpg',
        tracks=[
            TrackDTO(
                f'Track 0{i + 1}',
                number=i + 1,
                path='/music/Album2/Album.flac',
                offset=i * 5.0 * 60 if LIBROSA_AVAILABLE else None,
                duration=5.0 * 60 if LIBROSA_AVAILABLE else None,
            )
            for i in range(4, -1, -1)
        ],
    )

    album3 = AlbumDTO(
        title='The Title Of Album3',
        performer='The Performer',
        year=1969,
        path='/music/Album3/Album3.cue',
        cover='/music/Album3/Front.png',
        tracks=[
            TrackDTO(
                f'Track 0{i + 1}',
                number=i + 1,
                path=f'/music/Album3/Track0{i + 1}.flac',
                offset=0.0 if LIBROSA_AVAILABLE else None,
                duration=5.0 * 60 if LIBROSA_AVAILABLE else None,
            )
            for i in range(4, -1, -1)
        ],
    )

    album4 = AlbumDTO(
        title='The Title Of Album4',
        performer='The Performer',
        year=1970,
        path='/music/Album4/Album4.cue',
        cover='/music/Album4/Cover.jpg',
        tracks=[
            TrackDTO(
                f'Track 0{i + 1}',
                number=i + 1,
                path=f'/music/Album4/Side{"A" if i < 3 else "B"}.flac',
                offset=(i * 5.0 * 60 if i < 3 else (i - 3) * 5.0 * 60)
                if LIBROSA_AVAILABLE
                else None,
                duration=5.0 * 60 if LIBROSA_AVAILABLE else None,
            )
            for i in range(5, -1, -1)
        ],
    )

    album_list.append(album2)
    album_list.append(album3)
    album_list.append(album4)
    return album_list


@pytest.fixture()
def processed_album_dtos_w_status(processed_album_dtos):
    for i in processed_album_dtos:
        i.statuses.append(StatusDTO(status=Status.ADDED, success=Success.SUCCESS))
