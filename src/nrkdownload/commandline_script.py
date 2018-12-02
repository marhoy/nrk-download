# Python 2 compatibility
from __future__ import unicode_literals
from __future__ import print_function
from future.builtins import input

import argparse
import logging
import os.path
import platform
import re
import sys

# Our own modules
from nrkdownload import config
from nrkdownload import parse_nrk_url
from nrkdownload import version
from nrkdownload import download
from nrkdownload import tv
from nrkdownload import radio

LOG = logging.getLogger(__name__)


def make_parser():
    parser = argparse.ArgumentParser(
        description='Download series or programs from NRK, complete with images and'
                    ' subtitles.',
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
    parser.add_argument('-c', '--cache', action='store_true',
                        help="Enable persistent caching of the API requests.")

    mutex = parser.add_mutually_exclusive_group()
    mutex.add_argument('-a', '--all', action='store_true',
                       help="If URL matches several episodes: Download all episodes"
                            " without asking.")
    mutex.add_argument('-l', '--last', action='store_true',
                       help="If URL matches several episodes: Download the latest without"
                            " asking.")

    parser.add_argument('URL', nargs='*',
                        help="Specify download source(s). Browse https://tv.nrk.no/ or "
                             "https://radio.nrk.no/ and copy the URL. The URL can point"
                             " to a whole series, or just one episode.")

    parser.add_argument('-f', '--file',
                        help="Specify a file containing URLs, one URL per line. "
                             "Specifying urls from a file will automatically enable"
                             " --all and download all episodes from series.")
    return parser


def main():

    parser = make_parser()
    arguments = parser.parse_args()

    # Possibly change logging level of the top-level logger
    if arguments.verbose:
        if arguments.verbose == 1:
            logging.getLogger().setLevel(logging.INFO)
        if arguments.verbose >= 2:
            logging.getLogger().setLevel(logging.DEBUG)

    if arguments.d:
        config.DOWNLOAD_DIR = os.path.expanduser(arguments.d)

    config.ENABLE_CACHE = arguments.cache

    for url in arguments.URL:
        download_url(url, download_all=arguments.all, download_last=arguments.last)

    if arguments.file:
        if os.path.isfile(arguments.file):
            with open(arguments.file) as file:
                for line in file:
                    url = line.strip()
                    download_url(url, download_all=arguments.all,
                                 download_last=arguments.last)
        else:
            print("{} is not a valid filename".format(arguments.file))


def download_url(url, download_all=False, download_last=False):
    LOG.debug("Looking at %s", url)
    programs = parse_nrk_url.parse_url(url)
    programs = remove_unavailable_programs(programs)
    if len(programs) == 0:
        print("No programs available for download")
        return
    if len(programs) > 1:
        if (download_all is False) and (download_last is False):
            programs = ask_for_program_download(programs)
        elif download_last is True:
            programs = programs[-1:]
    if isinstance(programs[0], tv.Program):
        download.download_programs(programs)
    elif isinstance(programs[0], radio.PodcastEpisode):
        download.download_podcasts(programs)
    else:
        print("Program is of unknown type", type(programs[0]))


def remove_unavailable_programs(programs):
    available_programs = []
    for program in programs:
        if not program.media_urls:
            print("Not available for download: {}".format(program))
        else:
            available_programs.append(program)
    return available_programs


def get_slice_input(num_elements):
    while True:
        try:
            string = input(
                "\nEnter a number or Python-style interval (e.g. 8 or -2: or : )."
                " (q to quit): ")
            slice_match = re.match(r'^(-?\d*):(-?\d*)$', string)
            index_match = re.match(r'^(-?\d+)$', string)
            quit_match = re.match(r'^q$', string.lower())
            if slice_match:
                slice_min = int(slice_match.group(1) or 0)
                slice_max = int(slice_match.group(2) or num_elements)
            elif index_match:
                slice_min = int(index_match.group(1))
                if slice_min == -1:
                    slice_max = None
                else:
                    slice_max = slice_min + 1
            elif quit_match:
                print('OK, quitting program\n')
                sys.exit(0)
            else:
                raise SyntaxError('Syntax not allowed')
        except Exception as e:
            # An exception was generated above
            print('Sorry, not a valid input: {}\n'.format(e))
            continue
        else:
            # No exception generated above, we're done
            break

    s = slice(slice_min, slice_max)
    return s


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = get_slice_input(len(programs))
    LOG.debug('You selected %s', selection)
    return programs[selection]


if __name__ == '__main__':
    main()
