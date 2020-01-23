# These are needed if we are running under Python 2.7
from __future__ import unicode_literals
from __future__ import print_function

import logging

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:                                 # pragma: no cover
    # Python 2
    from urlparse import urlparse                   # noqa: F401

import re
import datetime
import dateutil.parser


# Module wide logger
LOG = logging.getLogger(__name__)


def valid_filename(string):
    filename = re.sub(r'[/\\?<>:*|!"\']', '', string)
    return filename


def create_image_url(image_id):
    return 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(image_id, 960)


def parse_datetime(string):
    return dateutil.parser.parse(string)


def zero_pad(value):
    try:
        return "{:02d}".format(int(value))
    except ValueError:
        return value


def parse_duration(string):
    # PT28M39S : 28m39s
    # PT3H12M41.6S : 3h12m41.6s
    if not string:
        LOG.warning('No duration given')
        return datetime.timedelta()

    hours = minutes = seconds = 0
    hours_search = re.search(r'(\d+)H', string)
    minutes_search = re.search(r'(\d+)M', string)
    seconds_search = re.search(r'([\d.]+)S', string)
    if hours_search:
        hours = int(hours_search.group(1))
    if minutes_search:
        minutes = int(minutes_search.group(1))
    if seconds_search:
        seconds = float(seconds_search.group(1))
    duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    return duration


def ffmpeg_seconds_downloaded(process):
    downloaded_time = datetime.timedelta()

    line = process.stderr.readline()
    if line:
        time_match = re.search(r'.+\s+time=([\d:.]+)', line)
        if time_match:
            downloaded_time_list = time_match.group(1).split(':')
            downloaded_time = datetime.timedelta(hours=int(downloaded_time_list[0]),
                                                 minutes=int(downloaded_time_list[1]),
                                                 seconds=float(downloaded_time_list[2]))

        # rate_match = re.search('\s+bitrate=([\d.]+)', line)
        # if rate_match:
        #    download_rate = rate_match.group(1)

    return downloaded_time.total_seconds()


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
