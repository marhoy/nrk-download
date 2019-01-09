# coding=UTF-8

import nrkdownload.download
import nrkdownload.parse_nrk_url
import nrkdownload.config


def test_download_programs(tmp_path):

    nrk_url = 'https://tv.nrk.no/serie/humorkalender/sesong/2/episode/24/avspiller'
    expected_files = [
        'Humorkalender/poster.jpg',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.m4v',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.jpg',
        'Humorkalender/Season 02/Humorkalender - S02E24 - Trond-Viggo - 24of24.no.srt'
    ]

    # Write downloads to the temporary directory
    nrkdownload.config.DOWNLOAD_DIR = tmp_path.as_posix()

    # Parse URL and download_all
    programs = nrkdownload.parse_nrk_url.parse_url(nrk_url)
    nrkdownload.download.download_programs(programs)

    # Check that expected files exists
    for file in expected_files:
        assert tmp_path.joinpath(file).exists()


def test_download_podcasts(tmp_path):

    nrk_url = 'https://radio.nrk.no/podkast/mandag_hele_aaret/nrkno-poddkast-26613-142282-09102018220300'  # noqa: E501
    expected_files = [
        'Mandag hele året/poster.jpg',
        'Mandag hele året/Mandag hele året - Episode 2 - Episode 15 Jeg vil kjøre formel 1 (2018-10-09).mp3'  # noqa: E501
    ]

    # Write downloads to the temporary directory
    nrkdownload.config.DOWNLOAD_DIR = tmp_path.as_posix()

    # Parse URL and download_all
    episodes = nrkdownload.parse_nrk_url.parse_url(nrk_url)
    nrkdownload.download.download_podcasts(episodes)

    # Check that expected files exists
    for file in expected_files:
        assert tmp_path.joinpath(file).exists()
