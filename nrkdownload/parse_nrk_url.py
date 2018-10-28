import re

# The urllib has changed from Python 2 to 3, and thus requires some extra handling
try:
    # Python 3
    from urllib.request import urlretrieve
    from urllib.parse import unquote, urlparse
except ImportError:
    # Python 2
    from urllib import unquote, urlretrieve
    from urlparse import urlparse

import nrkdownload.nrkapi
import nrkdownload.classes


def parse_url(url):
    """


    :param url:
    :return:
    """

    """
    An URL from tv.nrk.no could look like this:
    For a TV-series:
    https://tv.nrk.no/serie/oppfinneren

    For a season of a TV-series:
    https://tv.nrk.no/serie/oppfinneren/sesong/2

    For an episode of a season of a TV-series:
    https://tv.nrk.no/serie/oppfinneren/sesong/2/episode/2/avspiller
    https://tv.nrk.no/serie/oppfinneren/MKTV52000418
    https://tv.nrk.no/serie/forbrukerinspektoerene/MDHP11004318
    https://tv.nrk.no/serie/forbrukerinspektoerene/MDHP11004318/24-10-2018

    For a repeating TV-program
    https://tv.nrk.no/serie/ut-i-naturen/DVNA50000512
    https://tv.nrk.no/serie/ut-i-naturen/DVNA50000512/08-03-2016


    For a TV-program not part of a series
    https://tv.nrk.no/program/MYNR46000018
    https://tv.nrk.no/program/MYNR46000018/arif-og-unge-ferrari-med-stavanger-symfoniorkester
    https://tv.nrk.no/program/KMTE30000117
    https://tv.nrk.no/program/KMTE30000117/opproersskolen
    
    
    
    Radio:
    
    For a podcast with several episodes:
    https://radio.nrk.no/podkast/saann_er_du/
    
    For a specific podcast
    https://radio.nrk.no/podkast/saann_er_du/nrkno-poddkast-25555-141668-15092018140000
    
    """

    parsed_url = urlparse(url)

    series_match = re.match(r"/serie/([\w-]+)", parsed_url.path)
    season_match = re.match(r"/serie/[\w-]+/sesong/(\d+)", parsed_url.path)
    episode_match = re.match(r"/serie/[\w-]+/sesong/\d+/episode/(\d+)", parsed_url.path)
    episode_id_match = re.match(r"/serie/[\w-]+/(\w+)", parsed_url.path)
    program_match = re.match(r"/program/(\w+)", parsed_url.path)

    podcast_match = re.match(r"/podkast/([\w_-]+)", parsed_url.path)
    podcast_episode_match = re.match(r"/podkast/([\w_-]+)/([\w_-]+)", parsed_url.path)

    if episode_id_match and not episode_id_match.group(1) == "sesong":
        # This is a specific episode, and we know the mediaelement id
        episode = nrkdownload.classes.Program()
        return "Episode with ID {}".format(episode_id_match.group(1))

    if series_match and season_match and episode_match:
        return "Episode {}, Season {} of Series {}".format(episode_match.group(1),
                                                           season_match.group(1),
                                                           episode_match.group(1))

    if series_match and season_match:
        return "Season {} of series {}".format(season_match.group(1), series_match.group(1))

    if series_match and not season_match:
        return "Series with ID: {}".format(series_match.group(1))

    if program_match:
        return "Program with id {}".format(program_match.group(1))

    if podcast_episode_match:
        return "Podcast episode {} of podcast {}".format(podcast_episode_match.group(2),
                                                         podcast_episode_match.group(1))

    if podcast_match:
        return "Podcast {}".format(podcast_match.group(1))

# def download_from_url(url):
#
#     parsed_url = urlparse(url)
#
#     "https://tv.nrk.no/serie/p3-sjekker-ut/MYNT12000317/sesong-1/episode-3"
#     "https://tv.nrk.no/serie/paa-fylla"
#
#     # TODO: Format for episode URL have changed
#
#     series_match = re.match(r"/serie/([\w-]+)$", parsed_url.path)
#     program_match = re.match(r"/program/(\w+)", parsed_url.path)
#     episode_match = re.match(r"/serie/([\w-]+)/(\w+)", parsed_url.path)
#
#     if program_match:
#         series_id = None
#         program_id = program_match.group(1).lower()
#     elif episode_match:
#         series_id = episode_match.group(1)
#         program_id = episode_match.group(2).lower()
#     elif series_match:
#         series_id = series_match.group(1)
#         program_id = None
#     else:
#         LOG.error("Don't know what to do with URL: %s", url)
#         sys.exit(1)
#
#     if program_id:
#         try:
#             r = SESSION.get(NRK_PS_API + '/mediaelement/' + program_id)
#             r.raise_for_status()
#             json = r.json()
#             json['programId'] = program_id
#             json['imageId'] = json['image']['id']
#             program = new_program_from_search_result(json)
#             program.get_download_details(json=json)
#         except Exception as e:
#             LOG.error('Could not get program details: %s', e)
#             return
#
#         if program.media_urls:
#             download_programs([program])
#         else:
#             LOG.info('Sorry, program not available: %s', program.title)
#
#         if program.series_id:
#             series_id = program.series_id
#
#     elif series_id:
#         series = series_from_series_id(series_id)
#         download_series_metadata(series)
#         series.get_seasons_and_episodes()
#         episodes = [ep for season in series.seasons for ep in season.episodes]
#         download_programs(episodes)
#
#
#     """
#     https://tv.nrk.no/serie/paa-fylla
#     https://tv.nrk.no/serie/trygdekontoret/MUHH48000516/sesong-12/episode-5
#     https://tv.nrk.no/serie/trygdekontoret
#     https://tv.nrk.no/program/KOIF42005206/the-queen
#     https://tv.nrk.no/program/KOID20001217/geert-wilders-nederlands-hoeyrenasjonalist
#     https://tv.nrk.no/program/KOID76002309/the-act-of-killing
#     """
