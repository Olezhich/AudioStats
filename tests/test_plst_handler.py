def test_process_playlist_paths(plst_handler_instance, playlist, mock_files):
    app = plst_handler_instance

    res = set(i for i in app.process_playlist_paths(playlist))
    print(type(res))
    target = set()
    assert res == target