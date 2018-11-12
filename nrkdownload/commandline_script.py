#!/usr/bin/env python

import argparse
import os.path
import platform
import logging
import re
import sys

# Our own modules
from . import version
from . import tv
from . import utils
from . import config

LOG = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Download series or programs from NRK, complete with images and subtitles.',
        epilog='The files are by default downloaded to ~/Downloads/nrkdownload.'
               ' This can be changed by using the option -d as described above,'
               ' or you can define the environment variable NRKDOWNLOAD_DIR')

    parser.add_argument('--version', action='version',
                        version='%(prog)s version {}, running under {} with Python {}'.format(
                            version.version, platform.system(), platform.python_version()))
    parser.add_argument('-d', metavar='DIRECTORY', action='store',
                        help='The directory where the downloaded files will be placed')
    parser.add_argument('-v', '--verbose', action='count',
                        help="Increase verbosity. Can be repeated up to two times.")

    mutex = parser.add_mutually_exclusive_group()
    mutex.add_argument('-a', '--all', action='store_true',
                       help="If URL matches several episodes: Download all episodes without asking.")
    mutex.add_argument('-l', '--last', action='store_true',
                       help="If URL matches several episodes: Download the latest without asking.")

    parser.add_argument('URL', nargs='+',
                        help="Specify download source(s). Browse https://tv.nrk.no/ or https://radio.nrk.no/ and copy"
                             " the URL. The URL can point to a whole series, or just one episode.")

    arguments = parser.parse_args()

    # Possibly change logging level of the top-level logger
    if arguments.verbose:
        if arguments.verbose == 1:
            logging.getLogger().setLevel(logging.INFO)
        if arguments.verbose >= 2:
            logging.getLogger().setLevel(logging.DEBUG)

    if arguments.d:
        config.DOWNLOAD_DIR = os.path.expanduser(arguments.d)

    if arguments.all:
        config.DOWNLOAD_ALL = True

    if arguments.last:
        config.DOWNLOAD_LAST = True

    for url in arguments.URL:
        print(url)


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


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = get_slice_input(len(programs))
    LOG.debug('You selected %s', selection)

    print('Getting program details for your selection of {} programs...'.format(len(programs[selection])))
    programs_to_download = []
    # TODO: It takes time to call .get_download_details() sequentially. Should be rewritten to use parallel workers.
    for program in programs[selection]:
        program.get_download_details()
        if program.media_urls:
            programs_to_download.append(program)
            if program.series_id:
                series = tv.series_from_series_id(program.series_id)
                tv.download_series_metadata(series)
        else:
            LOG.info('Sorry, program not available: %s', program.title)

    tv.download_programs(programs_to_download)


if __name__ == '__main__':
    main()
