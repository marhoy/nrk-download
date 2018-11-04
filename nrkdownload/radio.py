# This is needed if we are running under Python 2.7
from __future__ import unicode_literals

import logging
import os.path

# Our own modules
from . import nrkapi
from . import utils
from . import config

# Module wide logger
LOG = logging.getLogger(__name__)


class Podcast:

    _known_podcasts = dict()

    def __init__(self, podcast_id, title, subtitle, image_url):
        self.podcast_id = podcast_id
        self.title = title
        self.subtitle = subtitle
        self.image_url = image_url
        self._episodes = None
        self.dir_name = utils.valid_filename(self.title)

        # Add our instance to dict with known podcasts
        self.add_known_podcast(podcast_id, self)

    @utils.ClassProperty
    def known_podcasts(cls):
        return cls._known_podcasts

    @classmethod
    def add_known_podcast(cls, podcast_id, podcast_obj):
        cls._known_podcasts[podcast_id] = podcast_obj

    @property
    def episodes(self):
        if not self._episodes:
            self._episodes = podcast_episodes(self.podcast_id)
        return self._episodes

    @episodes.setter
    def episodes(self, episodes):
        self._episodes = episodes


class PodcastEpisode:
    def __init__(self, podcast_id, episode_id, title, subtitle, duration, download_url, published):
        self.podcast_id = podcast_id
        self.episode_id = episode_id
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
        self.download_url = download_url
        self.published = published

    @property
    def podcast(self):
        return podcast_from_podcast_id(self.podcast_id)

    @property
    def episode_number(self):
        episode_ids = [episode.episode_id for episode in self.podcast.episodes]
        return episode_ids.index(self.episode_id)

    @property
    def filename(self):
        basedir = os.path.join(config.DOWNLOAD_DIR, self.podcast.dir_name)
        file = utils.valid_filename(self.__str__())
        string = os.path.join(basedir, file)
        return string

    def __str__(self):
        string = "{} - Episode {} ({}): {}".format(self.podcast.title,
                                                   self.episode_number + 1,
                                                   self.published.date(),
                                                   self.title
                                                   )
        return string


def podcast_from_podcast_id(podcast_id):
    if podcast_id in Podcast.known_podcasts:
        LOG.debug("Returning known podcast %s", podcast_id)
        return Podcast.known_podcasts[podcast_id]
    json = nrkapi.get_podcast_series(podcast_id)
    title = json['titles']['title']
    subtitle = json['titles']['subtitle']
    image_url = json['imageUrl']
    podcast = Podcast(podcast_id=podcast_id, title=title, subtitle=subtitle,
                      image_url=image_url)
    return podcast


def podcast_episodes(podcast_id):
    json = nrkapi.get_podcast_episodes(podcast_id)
    episodes = []
    for item in json['items']:
        episodes.append(podcast_episode_from_json(item))
    return episodes


def podcast_episode_from_json(json):
    if json['_links'].get('podcastEpisode'):
        url = json['_links']['podcastEpisode']['href']
    else:
        url = json['_links']['self']['href']
    episode_id = url.split('/')[-1]
    podcast_id = url.split('/')[-3]
    title = json['titles']['title']
    subtitle = json['titles']['subtitle']
    duration = utils.parse_duration(json['duration'])
    download_url = json['downloadables'][0]['audio']['url']
    published = utils.parse_datetime(json['publishedAt'])
    episode = PodcastEpisode(podcast_id=podcast_id, episode_id=episode_id, title=title,
                             subtitle=subtitle, duration=duration,
                             download_url=download_url, published=published)
    return episode


def episode_from_episode_id(podcast_id, episode_id):
    json = nrkapi.get_podcast_episode(podcast_id, episode_id)
    episode = podcast_episode_from_json(json)
    return episode
