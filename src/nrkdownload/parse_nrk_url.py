import logging
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

from . import tv
from . import radio

# Module wide logger
LOG = logging.getLogger(__name__)

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


def parse_url(url):
    """
    :param url:
    :return: program(s) or podcast(s)
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
        #   https://tv.nrk.no/serie/oppfinneren/MKTV52000418
        media_id = episode_id_match.group(1)
        episode = tv.new_program_from_mediaelement_id(media_id)
        LOG.info("URL matches episode %s", media_id)
        return [episode]

    if series_match and season_match and episode_match:
        # An episode of a series:
        # We know the season and episode number, but not the media id
        #   https://tv.nrk.no/serie/oppfinneren/sesong/2/episode/2/avspiller
        series_id = series_match.group(1)
        season_number = int(season_match.group(1))
        episode_number = int(episode_match.group(1))
        series = tv.series_from_series_id(series_id)
        episode = series.seasons[season_number - 1].episodes[episode_number - 1]
        LOG.info("URL matches episode %d, season %d of series %s",
                 episode_number, season_number, series_id)
        return [episode]

    if series_match and season_match:
        # A season of a series
        #   https://tv.nrk.no/serie/oppfinneren/sesong/2
        season_number = int(season_match.group(1))
        series_id = series_match.group(1)
        LOG.info("URL matches season number %d of series %s", season_number, series_id)
        series = tv.series_from_series_id(series_id)
        episodes = series.seasons[season_number - 1].episodes
        return episodes

    if series_match and not season_match:
        # This matches a whole series:
        #   https://tv.nrk.no/serie/oppfinneren
        series_id = series_match.group(1)
        series = tv.series_from_series_id(series_id)
        episodes = [episode for season in series.seasons for episode in season.episodes]
        LOG.info("URL matches series %s", series_id)
        return episodes

    if program_match:
        # This matches a specific program (not from a series)
        #   https://tv.nrk.no/program/MYNR46000018
        program_id = program_match.group(1)
        LOG.info("URL matches program with id %s", program_id)
        program = tv.new_program_from_mediaelement_id(program_id)
        return [program]

    if podcast_episode_match:
        # This matches a specific episode of a podcast
        #   https://radio.nrk.no/podkast/saann_er_du/nrkno-poddkast-25555-141668-15092018140000
        podcast_id = podcast_episode_match.group(1)
        episode_id = podcast_episode_match.group(2)
        episode = radio.episode_from_episode_id(podcast_id, episode_id)
        LOG.info("URL mathces episode %s of podcast %s", episode_id, podcast_id)
        return [episode]

    if podcast_match:
        # This matches a whole podcast, with many episodes
        #   https://radio.nrk.no/podkast/saann_er_du/
        podcast_id = podcast_match.group(1)
        podcast = radio.podcast_from_podcast_id(podcast_id)
        LOG.info("URL mathces podcast %s", podcast_id)
        return podcast.episodes
