#!/usr/bin/env python

import nrkrecorder

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='This script can be used to search tv.nrk.no and download programs.')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-s', '--series', action='store_true', help='Search for series')
    group1.add_argument('-p', '--program', action='store_true', help='Search for programs')
    parser.add_argument('search_string')
    arguments = parser.parse_args()

    nrkrecorder.search_from_cmdline(arguments)
