import io


def test_verbose(script_runner):
    ret = script_runner.run('nrkdownload', '-v')
    assert ret.success


def test_very_verbose(script_runner):
    ret = script_runner.run('nrkdownload', '-vv')
    assert ret.success


def test_download_url(script_runner, tmp_path):
    nrk_url = 'https://tv.nrk.no/serie/humorkalender/sesong/2'
    expected_files = [
        'Humorkalender/poster.jpg',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.m4v',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.jpg',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.no.srt'
    ]

    ret = script_runner.run('nrkdownload', nrk_url, '--last', '-d', tmp_path.as_posix())
    assert ret.success
    for file in expected_files:
        assert tmp_path.joinpath(file).exists()


def test_download_file(script_runner, tmp_path):
    ret = script_runner.run('nrkdownload', '-f', 'tests/test_urls.txt',
                            '--last', '-d', tmp_path.as_posix())
    assert ret.success
    ret = script_runner.run('nrkdownload', '-f', 'test_urls.txt',
                            '--last', '-d', tmp_path.as_posix())
    assert ret.success


def test_download_not_available(script_runner):
    url = 'https://tv.nrk.no/serie/maigret/sesong/2/episode/2'
    ret = script_runner.run('nrkdownload', url)
    assert ret.success


interactive_input = io.StringIO('-1\n')


# def test_download_url_interactive(script_runner, tmp_path, stdin=interactive_input):
#     nrk_url = 'https://tv.nrk.no/serie/humorkalender/sesong/2'
#     expected_files = [
#         'Humorkalender/poster.jpg',
#         'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.m4v',
#         'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.jpg',
#         'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.no.srt'
#     ]
#
#     ret = script_runner.run('nrkdownload', nrk_url, '-d', tmp_path.as_posix())
#     assert ret.success
#     for file in expected_files:
#         assert tmp_path.joinpath(file).exists()
