#!/usr/bin/env python

import argparse
import os.path

# Our own modules
import nrkdownload
from nrkdownload.version import version


def main():
    parser = argparse.ArgumentParser(
        description='Download series or programs from NRK, complete with images and subtitles.')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-s', '--series', action='store_true', help='Search for series')
    group1.add_argument('-p', '--program', action='store_true', help='Search for programs')
    parser.add_argument('search_string')
    parser.add_argument('-d', '--dir', metavar='DIRECTORY', action='store',
                        help='The directory where the downloaded files will be placed')
    parser.add_argument('--version', action='version', version='%(prog)s version ' + version)
    arguments = parser.parse_args()

    if arguments.dir:
        nrkdownload.DOWNLOAD_DIR = os.path.expanduser(arguments.dir)

    nrkdownload.search_from_cmdline(arguments)


if __name__ == '__main__':
    main()
