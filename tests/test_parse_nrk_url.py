# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import nrkdownload.config
import nrkdownload.parse_nrk_url


def test_parse_url():
    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren/MKTV52000418')
    assert len(programs) == 1

    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren/sesong/2/episode/2/avspiller')
    assert len(programs) == 1
    assert programs[0].title == 'Oppfinneren'
    assert programs[0].season_name == '2'
    assert programs[0].episode_number == 1
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Oppfinneren/Season 02/Oppfinneren - S02E02 - 2of8'
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Oppfinneren/Season 02/Oppfinneren - S02E02 - 2of8'
    assert programs[0].__str__() == 'Oppfinneren - Sesong 2 - Oppfinneren: 2:8'

    first_season = list(programs[0]._series.seasons.values())[0]
    assert first_season.__str__() == '1 (8 episoder)'

    assert programs[0]._series.__str__() == 'Oppfinneren : 3 Sesonger'
    nrkdownload.config.MAX_OUTPUT_STRING_LENGTH = 10
    assert programs[0].__str__() == 'Oppfinn...'

    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren/sesong/2')
    assert len(programs) == 8

    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren')
    assert len(programs) == 20

    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/program/MYNR46000018')
    assert len(programs) == 1
    assert programs[0].title == 'Arif og Unge Ferrari med Stavanger Symfoniorkester'
    assert programs[0].series_id is None
    assert programs[0].season_name is None
    assert programs[0].episode_number is None
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Arif og Unge Ferrari med Stavanger Symfoniorkester'

    podcasts = nrkdownload.parse_nrk_url.parse_url(
        'https://radio.nrk.no/podkast/mandag_hele_aaret/nrkno-poddkast-26613-142718-01112018083000')  # noqa: E501
    assert len(podcasts) == 1

    podcasts = nrkdownload.parse_nrk_url.parse_url(
        'https://radio.nrk.no/podkast/mandag_hele_aaret/')
    assert len(podcasts) == 6
    assert podcasts[1].title == 'Episode 1:5 "Jeg vil kjøre formel 1"'
    assert podcasts[1].podcast.title == 'Mandag hele året'
    assert podcasts[1].episode_number == 1
    assert podcasts[1].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Mandag hele året/Mandag hele året - Episode 2 - Episode 15 Jeg vil kjøre formel 1 (2018-10-09)'  # noqa: E501
