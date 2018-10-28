# This is needed if we are running under Python 2.7
from __future__ import unicode_literals

import logging
import os.path
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

# Our own modules
from . import utils
from . import config
from . import nrkapi


# Module wide logger
LOG = logging.getLogger(__name__)


class ClassProperty(property):
    """
    Python doesn't have class properties (yet?), but this should do the trick.
    We need this to keep track of known (previously seen) series.
    """
    def __get__(self, obj, obj_type=None):
        return super(ClassProperty, self).__get__(obj_type)

    def __set__(self, obj, value):
        super(ClassProperty, self).__set__(type(obj), value)

    def __delete__(self, obj):
        super(ClassProperty, self).__delete__(type(obj))


class Program:
    def __init__(self, program_id, title, description, image_url,
                 duration, media_urls, subtitle_urls,
                 series_id=None, episode_number_or_date=None, episode_title=None):
        LOG.info('Creating new Program: %s : %s', title, program_id)

        self.program_id = program_id
        self.title = title
        self.description = description
        self.image_url = image_url
        self.series_id = series_id
        self.episode_number_or_date = episode_number_or_date
        self.episode_title = episode_title
        self.media_urls = media_urls
        self.subtitle_urls = subtitle_urls
        self.duration = duration
        self._season_number = None
        self._episode_number = None
        self._filename = None

    @property
    def season_number(self):
        if not self._season_number:
            series = series_from_series_id(self.series_id)
            for i, season in enumerate(series.seasons):
                if self.program_id in season.episode_ids:
                    self._season_number = i
        return self._season_number

    @property
    def episode_number(self):
        if not self._episode_number:
            series = series_from_series_id(self.series_id)
            self._episode_number = series.seasons[self.season_number].episode_ids.index(self.program_id)
        return self._episode_number

    @property
    def filename(self):
        """
        This method either returns an already created filename, or it creates a new one.

        :return: filename: str
        """
        if self._filename:
            return self._filename

        if self.series_id:
            # This program is part of a series
            LOG.debug("Making filename for program %s", self.title)

            series = series_from_series_id(self.series_id)
            basedir = os.path.join(config.DOWNLOAD_DIR, series.dir_name,
                                   series.seasons[self.season_number].dir_name)

            filename = series.title
            filename += ' - S{:02}E{:02}'.format(self.season_number + 1,
                                                 self.episode_number + 1)

            if not self.title.lower().startswith(series.title.lower()):
                filename += ' - {}'.format(self.title)

            regex_match = re.match('^(\d+):(\d+)$', self.episode_number_or_date)
            if regex_match:
                filename += ' - {}of{}'.format(regex_match.group(1), regex_match.group(2))
            else:
                filename += ' - {}'.format(self.episode_number_or_date)
        else:
            # This program is not part of a series
            basedir = config.DOWNLOAD_DIR
            filename = self.title

        self._filename = os.path.join(basedir, utils.valid_filename(filename))
        return self._filename

    def __str__(self):
        string = ''
        if self.series_id:
            series = series_from_series_id(self.series_id)
            string += "{} - ".format(series.title)
        string += self.title
        if self.episode_number_or_date and not string.endswith(self.episode_number_or_date):
            string += ': ' + self.episode_number_or_date
        if len(string) > config.MAX_OUTPUT_STRING_LENGTH:
            string = string[:config.MAX_OUTPUT_STRING_LENGTH - 3] + '...'
        return string


class Season:
    def __init__(self, series_id, idx, season_id, name):
        LOG.info('Creating new season of %s: %s: %s: %s', series_id, idx, season_id, name)
        self.series_id = series_id
        self.idx = idx
        self.season_id = season_id
        self.name = name
        self._dir_name = None
        self._episode_ids = None
        self._episodes = None

    @property
    def dir_name(self):
        if not self._dir_name:
            self._dir_name = utils.valid_filename('Season {:02}'.format(self.idx + 1))
        # if not self.name.startswith('Sesong'):
        #     self._dir_name = utils.valid_filename(self._dir_name + '- {}'.format(self.name))
        return self._dir_name

    @property
    def episode_ids(self):
        if not self._episode_ids:
            LOG.info("Creating episode id list for season %s of series %s",
                     self.season_id, self.series_id)
            self._episode_ids = nrkapi.get_episode_ids_of_series_season(self.series_id,
                                                                        self.season_id)
        return self._episode_ids

    @property
    def episodes(self):
        if not self._episodes:
            LOG.info("Creating episode list for season %s of series %s",
                     self.season_id, self.series_id)
            self._episodes = [
                new_program_from_mediaelement_id(episode_id) for episode_id in self.episode_ids
            ]
        return self._episodes

    def __str__(self):
        string = '{}: {} ({} episoder)'.format(self.idx + 1, self.name, len(self.episode_ids))
        return string


class Series:
    # This property keeps track of the series we have seen so far
    _known_series = dict()

    def __init__(self, series_id, title, description, image_url, seasons):
        LOG.info('Creating new series: %s', series_id)

        self.series_id = series_id
        self.title = title
        self.description = description
        self.image_url = image_url
        self.seasons = seasons
        self.dir_name = utils.valid_filename(title)

        # Update the known series with our instance
        self.add_known_series(series_id, self)

    @ClassProperty
    def known_series(cls):
        return cls._known_series

    @classmethod
    def add_known_series(cls, series_id, series_obj):
        cls._known_series[series_id] = series_obj

    # @property
    # def seasonId2Idx(self):
    #     return {season.id: season.number for season in self.seasons}

    def __str__(self):
        string = '{} : {} Sesong'.format(self.title, len(self.seasons))
        if len(self.seasons) > 1:
            string += 'er'
        return string


def new_program_from_mediaelement_id(mediaelement_id, imagesize=960):
    json = nrkapi.get_mediaelement(mediaelement_id)
    program_id = mediaelement_id.upper()
    title = re.sub(r'\s+', ' ', json['title'])
    description = json['description']
    image_url = None
    for image in json['images']['webImages']:
        if image['pixelWidth'] == imagesize:
            image_url = image['imageUrl']
    series_id = json.get('seriesId', None)
    episode_number_or_date = json.get('episodeNumberOrDate', None)
    episode_title = json.get('episodeTitle', None)
    duration = utils.parse_duration(json.get('duration', None))
    media_urls = json.get('media_urls', [])
    subtitle_urls = json.get('subtitle_urls', [])

    program = Program(program_id=program_id,
                      title=title,
                      description=description,
                      image_url=image_url,
                      series_id=series_id,
                      duration=duration,
                      media_urls=media_urls,
                      subtitle_urls=subtitle_urls,
                      episode_number_or_date=episode_number_or_date,
                      episode_title=episode_title)
    return program


def series_from_series_id(series_id, image_size=960):
    if series_id in Series.known_series:
        LOG.info("Returning known series %s", series_id)
        return Series.known_series[series_id]

    json = nrkapi.get_series(series_id)
    title = json['title']
    description = json['description']
    image_url = None
    for image in json['image']['webImages']:
        if image['pixelWidth'] == image_size:
            image_url = image['imageUrl']

    seasons = []
    for idx, season in enumerate(json['seasons']):
        season_name = re.sub(r'\s+', ' ', season['name'])
        season_id = season['id']
        seasons.append(Season(series_id=series_id,
                              idx=idx,
                              season_id=season_id,
                              name=season_name))

    series = Series(series_id=series_id, title=title, description=description,
                    image_url=image_url, seasons=seasons)

    return series
