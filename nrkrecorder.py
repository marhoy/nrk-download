#!/usr/bin/env python

import nrkrecorder


def series_download(series):
    programs = []
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    nrkrecorder.ask_for_program_download(programs)


def search_from_cmdline(args):
    if args.series:
        series = nrkrecorder.search(args.search_string, 'series')
        if len(series) == 1:
            print('\nOnly one matching series')
            series_download(series[0])
        elif len(series) > 1:
            print('\nMatching series:')
            for i, s in enumerate(series):
                print('{:2}: {}'.format(i, s))
            index = nrkrecorder.get_integer_input(len(series) - 1)
            series_download(series[index])
        else:
            print('Sorry, no matching series')
    elif args.program:
        programs = nrkrecorder.search(args.search_string, 'program')
        if programs:
            nrkrecorder.ask_for_program_download(programs)
        else:
            print('Sorry, no matching programs')
    else:
        nrkrecorder.LOG.error('Unknown state, not sure what to do')


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='This script can be used to search tv.nrk.no and download programs.')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-s', '--series', action='store_true', help='Search for series')
    group1.add_argument('-p', '--program', action='store_true', help='Search for programs')
    parser.add_argument('search_string')
    arguments = parser.parse_args()

    search_from_cmdline(arguments)
