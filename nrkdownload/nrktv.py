import requests
import urllib.request
import urllib.parse
import os.path
import re
import sys
import datetime
import time
import multiprocessing
import subprocess
import tqdm

from . import utils, LOG
import nrkdownload

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

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
        self.imageUrl = utils.get_image_url(json['imageId'])
        self.seriesId = json.get('seriesId', None)
        self.episodeNumberOrDate = json.get('episodeNumberOrDate', None)
        self.episodeTitle = json.get('episodeTitle', None)
        self.isAvailable = False
        self.hasSubtitles = False
        self.mediaUrl = None
        self.subtitleUrl = None
        self.duration = datetime.timedelta()

        if self.seriesId and self.seriesId not in KNOWN_SERIES.keys():
            # This is an episode from a series we haven't seem yet
            LOG.debug('Program {} is from an unknown series {}'.format(self.programId, self.seriesId))
            Series(self.seriesId)

    def get_details(self):
        try:
            r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.programId)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            LOG.error('Could not get program details: {}'.format(e))
            return
        self.isAvailable = json['isAvailable']
        if self.isAvailable:
            self.mediaUrl = json.get('mediaUrl', None)
            if self.mediaUrl:
                self.mediaUrl = re.sub('\.net/z/', '.net/i/', self.mediaUrl)
                self.mediaUrl = re.sub('manifest\.f4m$', 'master.m3u8', self.mediaUrl)
            self.hasSubtitles = json.get('hasSubtitles', False)
            if self.hasSubtitles:
                self.subtitleUrl = urllib.parse.unquote(json['mediaAssets'][0]['webVttSubtitlesUrl'])
            self.duration = utils.parse_duration(json['duration'])

    def make_filename(self):
        if self.seriesId:
            series = KNOWN_SERIES[self.seriesId]
            season_number, episode_number = series.programIds[self.programId]
            basedir = os.path.join(nrkdownload.DOWNLOAD_DIR, series.dirName,
                                   series.seasons[season_number].dirName)

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
            basedir = nrkdownload.DOWNLOAD_DIR
            filename = self.title

        return os.path.join(basedir, utils.valid_filename(filename))

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
        self.dirName = utils.valid_filename('Season {:02}'.format(self.number + 1))
        if not self.name.startswith('Sesong'):
            self.dirName = utils.valid_filename(self.dirName + '- {}'.format(self.name))

    def __str__(self):
        string = '{}: {} ({} ep)'.format(self.number, self.name, len(self.episodes))
        return string


class Series:
    def __init__(self, series_id):
        LOG.info('Creating new series: {}'.format(series_id))

        # Register our seriesId. The object is updated later
        KNOWN_SERIES[series_id] = self

        try:
            r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            LOG.error('Not able get details for {}: {}'.format(series_id, e))
            sys.exit(1)

        self.seriesId = series_id
        self.title = re.sub('\s+', ' ', json['title'])
        self.description = json['description']
        self.imageUrl = utils.get_image_url(json['imageId'])
        self.dirName = utils.valid_filename(self.title)
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
        string = '{} : {} Sesong(er)'.format(self.title, len(self.seasons))
        return string


def search(search_string, search_type):
    try:
        r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + search_string)
        r.raise_for_status()
        json = r.json()
    except Exception as e:
        LOG.error('Not able to parse search-results: {}'.format(e))
        return

    series = programs = []
    hits = json.get('hits', [])
    if hits is None:
        hits = []
    for item in reversed(hits):
        if item['type'] == 'serie' and search_type == 'series':
            series.append(Series(item['hit']['seriesId']))
        elif item['type'] in ['program', 'episode'] and search_type == 'program':
            programs.append(Program(item['hit']))
        if item['type'] not in ['serie', 'program', 'episode']:
            LOG.warning('Unknown item type: {}'.format(item['type']))

    if search_type == 'series':
        return series
    elif search_type == 'program':
        return programs
    else:
        LOG.error('Unknown search type: {}'.format(search_type))


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = utils.get_slice_input(len(programs))
    LOG.debug('You selected {}'.format(selection))

    print('Getting program details for your selection of {} programs...'.format(len(programs[selection])))
    programs_to_download = []
    for program in programs[selection]:
        program.get_details()
        if program.isAvailable:
            programs_to_download.append(program)
            download_series_metadata(KNOWN_SERIES[program.seriesId])
        else:
            LOG.info('Sorry, program not available: {}'.format(program.title))

    download_programs(programs_to_download)


def download_worker(args):
    program, program_idx, progress_list = args
    program_filename = program.make_filename()
    download_dir = os.path.dirname(program_filename)
    image_filename = program_filename + '.jpg'
    subtitle_file = program_filename + '.no.srt'
    video_filename = program_filename + '.m4v'

    # Create directory if needed
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir, exist_ok=True)
        except Exception as e:
            LOG.error('Could not create directory {}: {}'.format(download_dir, e))
            return

    # Download image
    if not os.path.exists(image_filename):
        try:
            LOG.info('Downloading image for {}'.format(program.title))
            urllib.request.urlretrieve(program.imageUrl, image_filename)
        except Exception as e:
            LOG.warning('Could not download image for program {}: {}'.format(program.title, e))

    # Download subtitles
    if program.hasSubtitles and not os.path.exists(subtitle_file):
        LOG.info('Downloading subtitles for {}'.format(program.title))
        cmd = ['ffmpeg', '-loglevel', '8', '-i', program.subtitleUrl, subtitle_file]
        try:
            subprocess.run(cmd, stdin=subprocess.DEVNULL)
        except Exception as e:
            LOG.warning('Could not download subtitles for program {}: {}'.format(program.title, e))

    # Download video
    if not os.path.exists(video_filename):
        cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', program.mediaUrl]
        if os.path.exists(subtitle_file):
            cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0', 'language=nor']
        # cmd += ['-metadata', 'description="{}"'.format(obj.description)]
        # cmd += ['-metadata', 'track="24"']
        cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', video_filename]
        try:
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                                       universal_newlines=True)
            while process.poll() is None:
                seconds_downloaded = utils.ffmpeg_seconds_downloaded(process)
                progress_list[program_idx] = round(seconds_downloaded)
                time.sleep(0.5)
            process.wait()
        except Exception as e:
            LOG.warning('Unable to download program {}:{}: {}'.format(
                program.title, program.episodeTitle, e))


def download_programs(programs):
    total_duration = datetime.timedelta()
    for program in programs:
        total_duration += program.duration
    total_duration = total_duration - datetime.timedelta(microseconds=total_duration.microseconds)
    print('Ready to download {} programs, with total duration {}'.format(len(programs), total_duration))

    with multiprocessing.Pool(processes=os.cpu_count()) as pool, multiprocessing.Manager() as manager:

        shared_progress = manager.list([0]*len(programs))
        progress_bar = tqdm.tqdm(desc='Downloading', total=round(total_duration.total_seconds()),
                                 unit='s', unit_scale=True)

        LOG.debug('Starting pool of workers')
        args = [(program, idx, shared_progress) for idx, program in enumerate(programs)]
        result = pool.map_async(download_worker, args)

        while not result.ready():
            LOG.debug('Progress: {}'.format(shared_progress))
            time.sleep(0.1)
            progress_bar.update(sum(shared_progress) - progress_bar.n)
        progress_bar.update(progress_bar.total - progress_bar.n)
        progress_bar.close()

    LOG.debug('All workers finished. Result: {}'.format(result.get()))


def download_series_metadata(series):
    download_dir = os.path.join(nrkdownload.DOWNLOAD_DIR, series.dirName)
    image_filename = 'poster.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        LOG.info('Downloading image for series {}'.format(series.title))
        try:
            os.makedirs(download_dir, exist_ok=True)
            urllib.request.urlretrieve(series.imageUrl, os.path.join(download_dir, image_filename))
        except Exception as e:
            LOG.error('Could not download metadata for series {}: {}'.format(series.title, e))
