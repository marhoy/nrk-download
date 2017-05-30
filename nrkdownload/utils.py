# These are needed if we are running under Python 2.7
from __future__ import unicode_literals
from __future__ import print_function
from future.builtins import input

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

import re
import sys
import datetime

from . import LOG
import nrkdownload.nrktv  # We have to do it this way due to circular imports and Python2


def valid_filename(string):
    filename = re.sub(r'[/\\?<>:*|!"\']', '', string)
    return filename


def get_integer_input(max_allowed):
    while True:
        try:
            string = input('\nEnter a number in the range 0-{}. (q to quit): '.format(max_allowed))
            print(string)
            index_match = re.match(r'^(\d+)$', string)
            quit_match = re.match(r'^q$', string.lower())
            if index_match:
                index = int(index_match.group(1))
            elif quit_match:
                print('OK, quitting program\n')
                sys.exit(0)
            else:
                raise SyntaxError('Syntax not allowed')

            if index > max_allowed:
                raise ValueError('Value is too high')

        except Exception as e:
            # An exception was generated above
            print('Sorry, not a valid input: {}\n'.format(e))
            continue
        else:
            # No exception generated above, we're done
            break
    return index


def get_slice_input(num_elements):
    while True:
        try:
            string = input('\nEnter a number or interval (e.g. 8 or 5-10). (q to quit): ')
            slice_match = re.match(r'^(\d*)[:-](\d*)$', string)
            index_match = re.match(r'^(\d+)$', string)
            quit_match = re.match(r'^q$', string.lower())
            if slice_match:
                slice_min = int(slice_match.group(1) or 0)
                slice_max = int(slice_match.group(2) or num_elements - 1)
            elif index_match:
                slice_min = int(index_match.group(1))
                slice_max = slice_min
            elif quit_match:
                print('OK, quitting program\n')
                sys.exit(0)
            else:
                raise SyntaxError('Syntax not allowed')

            # Check the values of the ints
            if slice_min > slice_max:
                raise ValueError('Max is not larger than min')
            if slice_max >= num_elements or slice_min > num_elements - 1:
                raise ValueError('Value is too high')

        except Exception as e:
            # An exception was generated above
            print('Sorry, not a valid input: {}\n'.format(e))
            continue
        else:
            # No exception generated above, we're done
            break

    return slice(slice_min, slice_max + 1)


def get_image_url(image_id):
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
