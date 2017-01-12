#!/usr/bin/env python

import requests
import urllib.request
import os.path
import re
import sys
import logging

# Package-wide logging configuration
logging.basicConfig(format='{levelname}: {message}', level=logging.WARNING, style='{')
LOG = logging.getLogger()

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

# This is where the files end up
DOWNLOAD_DIR = os.path.expanduser('~/Downloads/nrktv')

KNOWN_SERIES = {}

# Initialize requests session
SESSION = requests.Session()
SESSION.headers['app-version-android'] = '999'


class Program:
    def __init__(self, json):

        LOG.debug('Creating new Program: {} : {}'.format(json['title'], json['programId']))

        self.programId = json['programId']
        self.title = re.sub('\s+', ' ', json['title'])
        self.description = json['description']
        self.imageId = json['imageId']
        self.seriesId = json.get('seriesId', None)
        self.episodeNumberOrDate = json.get('episodeNumberOrDate', None)
        self.episodeTitle = json.get('episodeTitle', None)

        if self.seriesId and self.seriesId not in KNOWN_SERIES.keys():
            # This is an episode from a series we haven't seem yet
            LOG.debug('Program {} is from an unknown series {}'.format(self.programId, self.seriesId))
            Series(self.seriesId)

    def get_details(self):
        r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.programId)
        r.raise_for_status()
        # self.json = r.json()
        # print(self.json, '\n\n')
        # isAvailable = eval(self.json['isAvailable'])
        # download_url = self.json['url']

    def make_filename(self):
        if self.seriesId:
            series = KNOWN_SERIES[self.seriesId]
            season_number, episode_number = series.programIds[self.programId]
            basedir = os.path.join(DOWNLOAD_DIR, series.dirName, series.seasons[season_number].dirName)

            filename = series.title
            filename += ' - S{:02}E{:02}'.format(season_number + 1, episode_number + 1)

            if not self.title.lower().startswith(series.title.lower()):
                filename += ' - {}'.format(self.title)

            regex_match = re.match('^(\d+):(\d+)$', self.episodeNumberOrDate)
            if regex_match:
                filename += ' - {}of{}'.format(regex_match.group(1), regex_match.group(2))
            else:
                filename += ' - {}'.format(self.episodeNumberOrDate)
        else:
            basedir = DOWNLOAD_DIR
            filename = self.title

        return os.path.join(basedir, safe_filename(filename))

    def __str__(self):
        if self.seriesId:
            series = KNOWN_SERIES[self.seriesId]
            season_number, episode_number = series.programIds[self.programId]
            string = '{} ({}): {} - {}'.format(
                series.title,
                series.seasons[season_number].name,
                self.title,
                self.episodeNumberOrDate)
            string += ' - S{:02}E{:02}'.format(season_number + 1, episode_number + 1)
            # string += '\n' + self.make_filename()
        else:
            string = self.title

        return string


class Season:
    def __init__(self, idx, json):
        LOG.info('Creating new season: {}: {}'.format(idx, json['name']))

        self.id = json['id']
        self.name = re.sub('\s+', ' ', json['name'])
        self.number = idx
        self.episodes = []
        self.dirName = safe_filename('Season {:02} - {}'.format(self.number + 1, self.name))

    def __str__(self):
        string = '{}: {} ({} ep)'.format(self.number, self.name, len(self.episodes))
        return string


class Series:
    def __init__(self, series_id):
        LOG.info('Creating new series: {}'.format(series_id))

        # Register our seriesId. The object is updated later
        KNOWN_SERIES[series_id] = self

        r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
        r.raise_for_status()
        json = r.json()

        self.seriesId = series_id
        self.title = re.sub('\s+', ' ', json['title'])
        self.description = json['description']
        self.imageId = json['imageId']
        self.dirName = safe_filename(self.title)
        self.seasons = []
        self.seasonId2Idx = {}
        self.programIds = {}
        self.json = json

        for idx, season in enumerate(reversed(json['seasonIds'])):
            self.seasons.append(Season(idx, season))
            self.seasonId2Idx[season['id']] = idx
        self.get_episodes()

        # Update the known series with our object
        KNOWN_SERIES[series_id] = self

    def get_episodes(self):
        for item in reversed(self.json['programs']):
            season_index = self.seasonId2Idx[item['seasonId']]
            program = Program(item)
            episode_number = len(self.seasons[season_index].episodes)
            LOG.debug('Series {}: Adding {} to S {}, E {}'.format(
                self.seriesId, program.title, season_index, episode_number))
            self.seasons[season_index].episodes.append(program)
            self.programIds[item['programId']] = (season_index, episode_number)

    def __str__(self):
        # string += '{}'.format([str(season) for season in self.seasons])
        string = '{} : {} Sesong(er)'.format(self.title, len(self.seasons))
        return string

    def download_metadata(self):
        download_dir = os.path.join(DOWNLOAD_DIR, self.dirName)
        os.makedirs(download_dir, exist_ok=True)
        image_url = 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(self.imageId, 960)
        urllib.request.urlretrieve(image_url, os.path.join(download_dir, 'show.jpg'))


def search(string, search_type):
    r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + string)
    r.raise_for_status()

    series = []
    programs = []
    for item in r.json()['hits']:
        if item['type'] == 'serie':
            if search_type == 'program':
                continue
            series_id = item['hit']['seriesId']
            series.append(Series(series_id))
        elif item['type'] in ['program', 'episode']:
            if search_type == 'series':
                continue
            programs.append(Program(item['hit']))
        else:
            LOG.warning('Unknown item type: {}'.format(item['type']))
    series.reverse()
    programs.reverse()

    return series, programs


def safe_filename(string):
    filename = re.sub(r'[/\\?<>:*|!"\']', '', string)
    return filename


def get_integer_input(max_allowed):
    while True:
        try:
            string = input('\nEnter a number in the range 0-{}. (q to quit): '.format(max_allowed))
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


def series_download(series):
    programs = []
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    ask_for_program_download(programs)


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = get_slice_input(len(programs))
    print('You selected {}'.format(selection))


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='This script can be used to search tv.nrk.no and download programs.')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-s', '--series', action='store_true', help='Search for series')
    group1.add_argument('-p', '--program', action='store_true', help='Search for programs')
    parser.add_argument('search_string')
    args = parser.parse_args()

    if args.series:
        series, _ = search(args.search_string, 'series')
        if len(series) == 1:
            print('\nOnly one matching series')
            series_download(series[0])
        elif len(series) > 1:
            print('\nMatching series:')
            for i, s in enumerate(series):
                print('{}: {}'.format(i, s))
            index = get_integer_input(len(series) - 1)
            series_download(series[index])
        else:
            print('Sorry, no matching series')
    elif args.program:
        _, programs = search(args.search_string, 'program')
        if programs:
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching series')
    else:
        LOG.error('Unknown state, not sure what to do')
