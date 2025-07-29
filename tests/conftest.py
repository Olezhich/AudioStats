import pytest
import tomlcfg
import logging

from audiostats.handlers import PlayListHandler


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
    return ['Album1.cue', 'Track1.flac', 'Album2.cue', 'Album3.cue']

@pytest.fixture()
def mock_files(monkeypatch):
    def mock_open(filename, *args, **kwargs):
        class MockFile:
            def __enter__(self):
                return self
            def __exit__(self, *args, **kwargs):
                pass
            def read(self):
                if filename == 'Album1.cue':
                    return ''
                if filename == 'Album2.cue':
                    return ''
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