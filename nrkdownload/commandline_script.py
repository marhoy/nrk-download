#!/usr/bin/env python

import argparse
import os.path

# Our own modules
import nrkdownload
from nrkdownload.version import version


def main():
    parser = argparse.ArgumentParser(
        description='Download series or programs from NRK, complete with images and subtitles.',
        epilog='The files are by default downloaded to ~/Downloads/nrkdownload.'
               ' This can be changed by using the option -d as described above,'
               ' or you can define the environment variable NRKDOWNLOAD_DIR')
    parser.add_argument('--version', action='version', version='%(prog)s version ' + version)
    parser.add_argument('-d', metavar='DIRECTORY', action='store',
                        help='The directory where the downloaded files will be placed')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-s', '--series', action='store_true', help='Search for series')
    group1.add_argument('-p', '--program', action='store_true', help='Search for programs')
    group1.add_argument('-u', '--url', action='store_true', help='The search_string is an URL')
    parser.add_argument_group('search_string', help='String')
    parser.add_argument('input', type=argparse.FileType('r'), default='-')
    #parser.add_argument('search_string',
    #                    help='Whatever you want to search for. Surround the string with single or'
    #                         ' double quotes if the string contains several words.')

    arguments = parser.parse_args()
    print(arguments)

    if arguments.d:
        nrkdownload.DOWNLOAD_DIR = os.path.expanduser(arguments.d)

    if arguments.series or arguments.program:
        nrkdownload.search_from_cmdline(arguments)

    if arguments.url:
        nrkdownload.parse_url(arguments)

if __name__ == '__main__':
    main()
