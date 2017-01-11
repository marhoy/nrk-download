#!/usr/bin/env python

import requests
import urllib.request
import os.path
import re
import sys

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
    def __init__(self, json, episode_idx=0, series=None, season=None):
        self.programId = json['programId']
        self.title = json['title']
        self.description = json['description']
        self.imageId = json['imageId']
        self.seriesTitle = json.get('seriesTitle', None)
        self.episodeNumberOrDate = json.get('episodeNumberOrDate', None)
        self.episodeTitle = json.get('episodeTitle', None)
        self.isAvailable = None

        if json.get('seriesId', None) and series is None:
            # This is an episode, but we don't have a Series-object
            self.series = Series(json.get('seriesId'))
        else:
            self.series = series

        self.season = season
        self.episode_idx = episode_idx
        self.json = json
        if series:
            print('Series: {}, Season: {}'.format(series.title, season.name))
        else:
            print('Program:')
        print(json, '\n\n')
        #self.get_details()

    def get_details(self):
        r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.programId)
        r.raise_for_status()
        self.json = r.json()
        print(self.json, '\n\n')
        #self.isAvailable = eval(self.json['isAvailable'])

        self.download_url = self.json['url']
        # self.seriesTitle = json['seriesTitle'] if json['seriesTitle'] != 'None' else ''
        # # self.seasonNumber = json['seasonNumber'] if json['seasonNumber'] != 'None' else ''
        self.episodeNumberOrDate = self.json.get('episodeNumberOrDate', '')

        # if self.episodeNumberOrDate and self.episodeNumberOrDate.find(':') > 0:
        #     self.s0xe0y = 'S' + self.seasonNumber.zfill(2) + 'E' + self.episodeNumberOrDate.split(':')[0].zfill(2)
        # else:
        #     self.s0xe0y = ''
        #
        # if self.seriesTitle and self.s0xe0y:
        #     self.fileName = os.path.join(self.seriesTitle, 'Season ' + self.seasonNumber.zfill(2),
        #                                  self.seriesTitle + ' - ' + self.s0xe0y + ' - ' + self.title)
        # elif self.seriesTitle:
        #     self.fileName = os.path.join(self.seriesTitle, 'Season ' + self.seasonNumber.zfill(2),
        #                                  self.seriesTitle + ' - ' + self.json['episodeTitle'])
        # else:
        #     self.fileName = os.path.join(self.title)

    def make_filename(self):
        filename = self.title
        if self.series:
            basedir = os.path.join(DOWNLOAD_DIR, self.series.dirName, self.season.dirName)
            if re.match('^\d+:\d+$', self.episodeNumberOrDate):
                filename += ' - S{:02}E{:02}'.format(self.season.number, self.episode_idx)
            else:
                filename += ' - {}'.format(self.episodeNumberOrDate)
        else:
            basedir = DOWNLOAD_DIR

        return os.path.join(basedir, filename)

    def __str__(self):
        string = 'ID: {}\n'.format(self.programId)
        string += '    Title: {}\n'.format(self.title)
        string += '    Episode: {}\n'.format(self.episodeNumberOrDate)
        #string += '    Filename: {}\n'.format(self.fileName)
        return string


class Season:
    def __init__(self, idx, json):
        self.id = json['id']
        self.name = json['name']
        self.number = idx + 1
        self.episodes = []
        if self.name.startswith('Sesong'):
            self.dirName = 'Season {:02}'.format(self.number)
        else:
            self.dirName = self.name

    def __str__(self):
        string = '{}: {} ({} ep)'.format(self.number, self.name, len(self.episodes))
        return string


class Series:
    def __init__(self, series_id):

        r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
        r.raise_for_status()
        json = r.json()

        self.seriesId = series_id
        self.title = json['title']
        self.description = json['description']
        self.imageId = json['imageId']
        self.dirName = self.title
        self.seasons = []
        self.seasonId2Idx = {}
        self.json = json

        for idx, season in enumerate(reversed(json['seasonIds'])):
            self.seasons.append(Season(idx, season))
            self.seasonId2Idx[season['id']] = idx
        self.get_episodes()

        if series_id not in KNOWN_SERIES.keys():
            KNOWN_SERIES[series_id] = self

    def get_episodes(self):
        for idx, item in enumerate(reversed(self.json['programs'])):
            season_index = self.seasonId2Idx[item['seasonId']]
            program = Program(item, idx, series=self, season=self.seasons[season_index])
            self.seasons[season_index].episodes.append(program)

    def __str__(self):
        string = 'SeriesID: {}\n'.format(self.seriesId)
        string += '    Title: {}\n'.format(self.title)
        string += '    Seasons: '
        string += '{}'.format([str(season) for season in self.seasons])
        return string

    def download_metadata(self):
        download_dir = os.path.join(DOWNLOAD_DIR, self.dirName)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        image_url = 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(self.imageId, 960)
        urllib.request.urlretrieve(image_url, os.path.join(download_dir, 'show.jpg'))


def search(string):
    r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + string)
    r.raise_for_status()

    series = []
    programs = []
    for item in r.json()['hits']:
        series_id = item['hit']['seriesId']
        if item['type'] == 'serie':
            series.append(Series(series_id))
        elif item['type'] in ['program', 'episode']:
            programs.append(Program(item['hit']))
    series.reverse()
    programs.reverse()
    return series, programs


def get_slice_input(num_elements):
    while True:
        try:
            string = input('Enter a number or interval (e.g. 8 or 5-10). (q to quit): ')
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


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='This script can be used to search tv.nrk.no and download programs.')
    parser.add_argument('search_string', help='The string to search for on tv.nrk.no')
    args = parser.parse_args()

    series, programs = search(args.search_string)
    for p in programs:
#        print(p.make_filename())
        print(p)
    for i, s in enumerate(series):
        print(i, s)
