
def test_process_playlist_paths(plst_handler_instance, playlist, mock_files, mock_listdir, mock_get_duration, processed_album_dtos):
    app = plst_handler_instance

    res = [i for i in app.process_playlist_paths(playlist)]
    target = processed_album_dtos
    assert target[0] == res[0], 'one cue one flac'
    assert target[1] == res[1], 'one track one flac'
    assert target[2] == res[2], 'one side one flac'