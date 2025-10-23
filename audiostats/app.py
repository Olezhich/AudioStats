import tomlcfg
import handlers


class App(tomlcfg.BaseModel):
    def __init__(self):
        super().__init__('./config/config.toml')
        self._PlayListHandler = handlers.PlayListHandler(self._config['PlayList'])

    def update_playlist(self, playlist: list[str]):
        """called when updating a playlist to enter data about new objects in the music library into db"""
        # do smth business logic
