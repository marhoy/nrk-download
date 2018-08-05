# These are needed if we are running under Python 2.7
from __future__ import unicode_literals
from __future__ import print_function
from future.builtins import input

import logging

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

import re
import sys
import datetime

import nrkdownload.nrktv  # We have to do it this way due to circular imports and Python2

# Module wide logger
LOG = logging.getLogger(__name__)


def valid_filename(string):
    filename = re.sub(r'[/\\?<>:*|!"\']', '', string)
    return filename


def create_image_url(image_id):
    return 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(image_id, 960)


def parse_duration(string):
    # PT28M39S : 28m39s
    # PT3H12M41.6S : 3h12m41.6s
    hours = minutes = seconds = 0
    hours_search = re.search('(\d+)H', string)
    minutes_search = re.search('(\d+)M', string)
    seconds_search = re.search('([\d.]+)S', string)
    if hours_search:
        hours = int(hours_search.group(1))
    if minutes_search:
        minutes = int(minutes_search.group(1))
    if seconds_search:
        seconds = float(seconds_search.group(1))

    try:
        duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except Exception as e:
        LOG.warning('Unable to calculate duration: %s: %s', string, e)
        return datetime.timedelta()

    return duration


def ffmpeg_seconds_downloaded(process):
    downloaded_time = datetime.timedelta()

    line = process.stderr.readline()
    if line:
        time_match = re.search('.+\s+time=([\d:.]+)', line)
        if time_match:
            downloaded_time_list = time_match.group(1).split(':')
            downloaded_time = datetime.timedelta(hours=int(downloaded_time_list[0]),
                                                 minutes=int(downloaded_time_list[1]),
                                                 seconds=float(downloaded_time_list[2]))

        # rate_match = re.search('\s+bitrate=([\d.]+)', line)
        # if rate_match:
        #    download_rate = rate_match.group(1)

    return downloaded_time.total_seconds()


def parse_urls(args):

    if is_valid_url(args.url):
        nrkdownload.nrktv.download_from_url(args.url)
    else:
        try:
            file = open(args.url, 'r')
        except FileNotFoundError:
            LOG.error("The string %s is neither a valid URL nor a valid filename", args.url)
            sys.exit(1)

        for line in file:
            line = line.strip()
            if is_valid_url(line):
               nrkdownload.nrktv.download_from_url(line)
            else:
                LOG.warning("Skipping invalid URL: %s", line)


def is_valid_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == "tv.nrk.no" and parsed_url.scheme == 'https' \
       and parsed_url.path.startswith(('/serie/', '/program/')):
        return True
    else:
        return False
