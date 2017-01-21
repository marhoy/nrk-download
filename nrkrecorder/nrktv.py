import nrkrecorder

import requests
import urllib.request
import urllib.parse
import os.path
import re
import sys
import subprocess

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

KNOWN_SERIES = {}

# Initialize requests session
SESSION = requests.Session()
SESSION.headers['app-version-android'] = '999'


class Program:
    def __init__(self, json):

        nrkrecorder.LOG.debug('Creating new Program: {} : {}'.format(json['title'], json['programId']))

        self.programId = json['programId']
        self.title = re.sub('\s+', ' ', json['title'])
        self.description = json['description']
        self.imageUrl = nrkrecorder.utils.get_image_url(json['imageId'])
        self.seriesId = json.get('seriesId', None)
        self.episodeNumberOrDate = json.get('episodeNumberOrDate', None)
        self.episodeTitle = json.get('episodeTitle', None)
        self.isAvailable = False
        self.hasSubtitles = False
        self.downloadUrl = None
        self.subtitleUrl = None

        if self.seriesId and self.seriesId not in KNOWN_SERIES.keys():
            # This is an episode from a series we haven't seem yet
            nrkrecorder.LOG.debug('Program {} is from an unknown series {}'.format(self.programId, self.seriesId))
            Series(self.seriesId)

    def get_details(self):
        try:
            r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.programId)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            nrkrecorder.LOG.error('Could not get program details: {}'.format(e))
            return
        self.isAvailable = json['isAvailable']
        self.hasSubtitles = json['hasSubtitles']
        self.downloadUrl = json['mediaUrl']
        if self.hasSubtitles:
            self.subtitleUrl = urllib.parse.unquote(json['mediaAssets'][0]['webVttSubtitlesUrl'])

    def make_filename(self):
        if self.seriesId:
            series = KNOWN_SERIES[self.seriesId]
            season_number, episode_number = series.programIds[self.programId]
            basedir = os.path.join(nrkrecorder.DOWNLOAD_DIR, series.dirName, series.seasons[season_number].dirName)

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
            basedir = nrkrecorder.DOWNLOAD_DIR
            filename = self.title

        return os.path.join(basedir, nrkrecorder.utils.valid_filename(filename))

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
        nrkrecorder.LOG.info('Creating new season: {}: {}'.format(idx, json['name']))

        self.id = json['id']
        self.name = re.sub('\s+', ' ', json['name'])
        self.number = idx
        self.episodes = []
        self.dirName = nrkrecorder.utils.valid_filename('Season {:02} - {}'.format(self.number + 1, self.name))

    def __str__(self):
        string = '{}: {} ({} ep)'.format(self.number, self.name, len(self.episodes))
        return string


class Series:
    def __init__(self, series_id):
        nrkrecorder.LOG.info('Creating new series: {}'.format(series_id))

        # Register our seriesId. The object is updated later
        KNOWN_SERIES[series_id] = self

        r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
        r.raise_for_status()
        json = r.json()

        self.seriesId = series_id
        self.title = re.sub('\s+', ' ', json['title'])
        self.description = json['description']
        self.imageUrl = nrkrecorder.utils.get_image_url(json['imageId'])
        self.dirName = nrkrecorder.utils.valid_filename(self.title)
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
            nrkrecorder.LOG.debug('Series {}: Adding {} to S {}, E {}'.format(
                self.seriesId, program.title, season_index, episode_number))
            self.seasons[season_index].episodes.append(program)
            self.programIds[item['programId']] = (season_index, episode_number)

    def __str__(self):
        # string += '{}'.format([str(season) for season in self.seasons])
        string = '{} : {} Sesong(er)'.format(self.title, len(self.seasons))
        return string


def search(string, search_type):
    try:
        r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + string)
        r.raise_for_status()
        json = r.json()
    except Exception as e:
        nrkrecorder.LOG.error('Not able to parse search-results: {}'.format(e))
        sys.exit(1)

    series = []
    programs = []
    for item in json['hits']:
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
            nrkrecorder.LOG.warning('Unknown item type: {}'.format(item['type']))
    series.reverse()
    programs.reverse()

    return series, programs


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
    selection = nrkrecorder.get_slice_input(len(programs))
    print('You selected {}'.format(selection))

    programs_to_download = []
    for program in programs[selection]:

        program.get_details()
        if program.isAvailable:
            programs_to_download.append(program)
            download_series_metadata(KNOWN_SERIES[program.seriesId])
        else:
            nrkrecorder.LOG.info('Sorry, program not available: {}'.format(program.title))

    download_programs_in_parallel(programs_to_download)


def download_worker(args):
    index, program, progress_list = args


def download_programs_in_parallel(programs):
    pass


def download_series_metadata(series):
    download_dir = os.path.join(nrkrecorder.DOWNLOAD_DIR, series.dirName)
    image_filename = 'show.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        nrkrecorder.LOG.info('Downloading image for series {}'.format(series.title))
        os.makedirs(download_dir, exist_ok=True)
        urllib.request.urlretrieve(series.imageUrl, os.path.join(download_dir, image_filename))


def download(obj, json=None):
    image_url = nrkrecorder.utils.get_image_url(obj.imageId)
    if type(obj) == Series:
        download_dir = os.path.join(nrkrecorder.DOWNLOAD_DIR, obj.dirName)
        image_filename = 'show.jpg'
    elif type(obj) == Program:
        program_filename = obj.make_filename()
        download_dir = os.path.dirname(program_filename)
        image_filename = os.path.basename(program_filename) + '.jpg'
    else:
        nrkrecorder.LOG.error('Download: Unkown datatype: {}'.format(type(obj)))
        return

    # Download images
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        nrkrecorder.LOG.info('Downloading image for {}'.format(type(obj)))
        os.makedirs(download_dir, exist_ok=True)
        urllib.request.urlretrieve(image_url, os.path.join(download_dir, image_filename))

    # We're done with Series, the rest is regarding Programs
    if type(obj) == Series:
        return

    # Download subtitles
    program_filename = obj.make_filename()
    mp4_filename = program_filename + '.mp4'
    subtitle_file = program_filename + '.no.srt'
    if json['hasSubtitles'] and not os.path.exists(subtitle_file):
        print('Downloading subtitles')
        cmd = ['ffmpeg', '-loglevel', '8',
               '-i', urllib.parse.unquote(json['mediaAssets'][0]['webVttSubtitlesUrl']),
               subtitle_file]
        subprocess.run(cmd, stderr=subprocess.DEVNULL)

    # Download video
    if json['mediaUrl'] and not os.path.exists(mp4_filename):
        video_url = json['mediaUrl']
        video_url = re.sub('\.net/z/', '.net/i/', video_url)
        video_url = re.sub('manifest\.f4m$', 'master.m3u8', video_url)
        cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', video_url]
        if os.path.exists(subtitle_file):
            cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0', 'language=nor']
        cmd += ['-metadata', 'description="{}"'.format(obj.description)]
        cmd += ['-metadata', 'track="24"']
        cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', mp4_filename]
        subprocess.run(cmd)

    # Remove subtitle file after including it in the mp4 video
    if os.path.exists(subtitle_file) and os.path.exists(mp4_filename):
        os.remove(subtitle_file)


def search_from_cmdline(args):
    if args.series:
        series, _ = search(args.search_string, 'series')
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
        _, programs = search(args.search_string, 'program')
        if programs:
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching series')
    else:
        nrkrecorder.LOG.error('Unknown state, not sure what to do')
