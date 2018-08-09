#!/usr/bin/env python

import argparse
import os.path
import platform
import logging
import re
import sys

# Our own modules
from . import version
from . import nrktv
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

    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument('-p', '--program',
                       help="Search for a program that matches the string PROGRAM. Interactive download.")
    mutex.add_argument('-s', '--series',
                       help="Search for a series that matches the string SERIES. Interactive download")
    mutex.add_argument('-u', '--url',
                       help="Download whatever is specified by URLs, no questions asked. "
                            "URLs can be copied from https://tv.nrk.no/")

    arguments = parser.parse_args()

    # Possibly change logging level of the top-level logger
    if arguments.verbose:
        if arguments.verbose == 1:
            logging.getLogger().setLevel(logging.INFO)
        if arguments.verbose >= 2:
            logging.getLogger().setLevel(logging.DEBUG)

    if arguments.d:
        config.DOWNLOAD_DIR = os.path.expanduser(arguments.d)

    if arguments.series or arguments.program:
        search_from_cmdline(arguments)

    if arguments.url:
        utils.parse_urls(arguments)


def search_from_cmdline(args):
    if args.series:
        matching_series = nrktv.search(args.series, 'series')
        if len(matching_series) == 1:
            print('\nOnly one matching series: {}'.format(matching_series[0].title))
            programs = nrktv.find_all_episodes(matching_series[0])
            ask_for_program_download(programs)
        elif len(matching_series) > 1:
            print('\nMatching series:')
            for i, s in enumerate(matching_series):
                print('{:2}: {}'.format(i, s))
            index = get_integer_input(len(matching_series) - 1)
            programs = nrktv.find_all_episodes(matching_series[index])
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching series')
    elif args.program:
        programs = nrktv.search(args.program, 'program')
        if programs:
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching programs')
    else:
        LOG.error('Unknown state, not sure what to do')


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
        if program.isAvailable:
            programs_to_download.append(program)
            if program.seriesId:
                nrktv.download_series_metadata(nrktv.Series.known_series[program.seriesId])
        else:
            LOG.info('Sorry, program not available: %s', program.title)

    nrktv.download_programs_in_parallel(programs_to_download)


if __name__ == '__main__':
    main()
