import nrkrecorder

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
        self.duration = datetime.timedelta()

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
        self.downloadUrl = json['mediaUrl']
        self.hasSubtitles = json['hasSubtitles']
        if self.hasSubtitles:
            self.subtitleUrl = urllib.parse.unquote(json['mediaAssets'][0]['webVttSubtitlesUrl'])
        self.duration = nrkrecorder.utils.parse_duration(json['duration'])

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

        try:
            r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            nrkrecorder.LOG.error('Not able get details for {}: {}'.format(series_id, e))
            sys.exit(1)

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
        string = '{} : {} Sesong(er)'.format(self.title, len(self.seasons))
        return string


def search(search_string, search_type):
    try:
        r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + search_string)
        r.raise_for_status()
        json = r.json()
    except Exception as e:
        nrkrecorder.LOG.error('Not able to parse search-results: {}'.format(e))
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
            nrkrecorder.LOG.warning('Unknown item type: {}'.format(item['type']))

    if search_type == 'series':
        return series
    elif search_type == 'program':
        return programs
    else:
        nrkrecorder.LOG.error('Unknown search type: {}'.format(search_type))


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = nrkrecorder.get_slice_input(len(programs))
    nrkrecorder.LOG.debug('You selected {}'.format(selection))

    programs_to_download = []
    for program in programs[selection]:

        program.get_details()
        if program.isAvailable:
            programs_to_download.append(program)
            download_series_metadata(KNOWN_SERIES[program.seriesId])
        else:
            nrkrecorder.LOG.info('Sorry, program not available: {}'.format(program.title))

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
            nrkrecorder.LOG.error('Could not create directory {}: {}'.format(download_dir, e))
            return

    # Download image
    if not os.path.exists(image_filename):
        try:
            nrkrecorder.LOG.info('Downloading image for {}'.format(program.title))
            urllib.request.urlretrieve(program.imageUrl, os.path.join(download_dir, image_filename))
        except Exception as e:
            nrkrecorder.LOG.warning('Could not download image for program {}: {}'.format(program.title, e))

    # Download subtitles
    if program.hasSubtitles and not os.path.exists(subtitle_file):
        nrkrecorder.LOG.info('Downloading subtitles for {}'.format(program.title))
        cmd = ['ffmpeg', '-loglevel', '8', '-i', program.subtitleUrl, subtitle_file]
        try:
            subprocess.run(cmd, stdin=subprocess.DEVNULL)
        except Exception as e:
            nrkrecorder.LOG.warning('Could not download subtitles for program {}: {}'.format(program.title, e))

    progress_list[program_idx] = 1
    return program_idx

    # # Download video
    # if json['mediaUrl'] and not os.path.exists(mp4_filename):
    #     video_url = json['mediaUrl']
    #     video_url = re.sub('\.net/z/', '.net/i/', video_url)
    #     video_url = re.sub('manifest\.f4m$', 'master.m3u8', video_url)
    #     cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', video_url]
    #     if os.path.exists(subtitle_file):
    #         cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0', 'language=nor']
    #     cmd += ['-metadata', 'description="{}"'.format(obj.description)]
    #     cmd += ['-metadata', 'track="24"']
    #     cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', mp4_filename]
    #     subprocess.run(cmd)


def download_programs(programs):
    total_duration = datetime.timedelta()
    for program in programs:
        total_duration += program.duration
    total_duration = total_duration - datetime.timedelta(microseconds=total_duration.microseconds)
    print('Ready to download {} programs, with total duration {}'.format(len(programs), total_duration))

    with multiprocessing.Pool(processes=8) as pool, multiprocessing.Manager() as manager:

        shared_progress = manager.list([0]*len(programs))
        progress_bar = tqdm.tqdm(desc='Downloading', total=round(total_duration.total_seconds()), unit='s')

        nrkrecorder.LOG.debug('Starting pool of {} workers'.format(pool._processes))
        args = [(program, idx, shared_progress) for idx, program in enumerate(programs)]
        result = pool.map_async(download_worker, args)

        while not result.ready():
            nrkrecorder.LOG.debug('Progress: {}'.format(shared_progress))
            time.sleep(0.1)
            progress_bar.update(sum(shared_progress) - progress_bar.n)
        # progress_bar.update(progress_bar.total - progress_bar.n)
        progress_bar.close()

    nrkrecorder.LOG.debug('All workers finished. Result: {}'.format(result.get()))


def download_series_metadata(series):
    download_dir = os.path.join(nrkrecorder.DOWNLOAD_DIR, series.dirName)
    image_filename = 'show.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        nrkrecorder.LOG.info('Downloading image for series {}'.format(series.title))
        try:
            os.makedirs(download_dir, exist_ok=True)
            urllib.request.urlretrieve(series.imageUrl, os.path.join(download_dir, image_filename))
        except Exception as e:
            nrkrecorder.LOG.error('Could not download metadata for series {}: {}'.format(series.title, e))
            sys.exit(1)


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