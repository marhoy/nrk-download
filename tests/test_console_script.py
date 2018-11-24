
def test_nrkdownload_version(script_runner):
    ret = script_runner.run('nrkdownload', '--version')
    assert ret.success


def test_nrkdownload_download(script_runner, tmp_path):
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
