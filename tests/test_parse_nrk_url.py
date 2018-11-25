import nrkdownload.parse_nrk_url
import nrkdownload.config


def test_parse_url():
    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren/MKTV52000418')
    assert len(programs) == 1

    programs = nrkdownload.parse_nrk_url.parse_url(
        'https://tv.nrk.no/serie/oppfinneren/sesong/2/episode/2/avspiller')
    assert len(programs) == 1
    assert programs[0].title == 'Oppfinneren'
    assert programs[0].season_number == 1
    assert programs[0].episode_number == 1
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Oppfinneren/Season 02/Oppfinneren - S02E02 - 2of8'
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Oppfinneren/Season 02/Oppfinneren - S02E02 - 2of8'
    assert programs[0].__str__() == 'Oppfinneren - Sesong 2 - Oppfinneren: 2:8'
    assert programs[0]._series.seasons[0].__str__() == '1: 1 (8 episoder)'
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
    assert programs[0].season_number is None
    assert programs[0].episode_number is None
    assert programs[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Arif og Unge Ferrari med Stavanger Symfoniorkester'

    podcasts = nrkdownload.parse_nrk_url.parse_url(
        'https://radio.nrk.no/podkast/saann_er_du/nrkno-poddkast-25555-141668-15092018140000')
    assert len(podcasts) == 1

    podcasts = nrkdownload.parse_nrk_url.parse_url(
        'https://radio.nrk.no/podkast/saann_er_du/')
    assert len(podcasts) == 36
    assert podcasts[0].title == 'Sånn er du, Karl Ove Knausgård'
    assert podcasts[0].podcast.title == 'Sånn er du'
    assert podcasts[0].episode_number == 0
    assert podcasts[0].filename == nrkdownload.config.DOWNLOAD_DIR + \
        '/Sånn er du/Sånn er du - Episode 1 (2017-01-08)'
