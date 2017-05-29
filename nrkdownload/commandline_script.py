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

    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument('-p', '--program',
                       help="Search for a program that matches the string PROGRAM. Interactive download.")
    mutex.add_argument('-s', '--series',
                       help="Search for a series that matches the string SERIES. Interactive download")
    mutex.add_argument('-u', '--url',
                       help="Download whatever is specified by URLs, no questions asked. "
                            "URLs can be copied from https://tv.nrk.no/")

    arguments = parser.parse_args()

    if arguments.d:
        nrkdownload.DOWNLOAD_DIR = os.path.expanduser(arguments.d)

    if arguments.series or arguments.program:
        nrkdownload.search_from_cmdline(arguments)

    if arguments.url:
        nrkdownload.parse_urls(arguments)


if __name__ == '__main__':
    main()
