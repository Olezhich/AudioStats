import pytest
import tomlcfg

from audiostats.handlers import PlayListHandler


@pytest.fixture
def plst_handler_instance():
    class PlstHandlerApp(tomlcfg.BaseModel):
        def __init__(self):
            super().__init__('./config/config.toml')
            self.plst_handler = PlayListHandler(self._config['PlayList'])
    app = PlstHandlerApp()
    return app.plst_handler