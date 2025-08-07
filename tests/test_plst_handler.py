
def test_process_playlist_paths(plst_handler_instance, playlist, mock_files, mock_listdir, mock_get_duration, processed_album_dtos):
    app = plst_handler_instance

    res = [i for i in app.process_playlist_paths(playlist)]
    target = processed_album_dtos
    assert target == res