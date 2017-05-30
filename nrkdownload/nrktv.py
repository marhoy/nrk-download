# This is needed if we are running under Python 2.7
from __future__ import unicode_literals

import requests
import os.path
import re
import sys
import datetime
import time
import multiprocessing
import subprocess
import tqdm

# The urllib has changed from Python 2 to 3, and thus requires some extra handling
try:
    # Python 3
    from urllib.request import urlretrieve
    from urllib.parse import unquote, urlparse
except ImportError:
    # Python 2
    from urllib import unquote, urlretrieve
    from urlparse import urlparse

# Our own modules
from . import LOG
from . import utils
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
        LOG.debug('Creating new Program: %s : %s', json['title'], json['programId'])
        self.programId = json['programId'].lower()
        self.title = re.sub(r'\s+', ' ', json['title'])
        self.description = json['description']
        self.imageUrl = utils.get_image_url(json['imageId'])
        self.seriesId = json.get('seriesId', None)
        self.episodeNumberOrDate = json.get('episodeNumberOrDate', None)
        self.episodeTitle = json.get('episodeTitle', None)
        self.isAvailable = False
        self.hasSubtitles = False
        self.mediaUrl = None
        self.subtitleUrl = None
        self.filename = ''
        self.duration = datetime.timedelta()

        if self.seriesId and self.seriesId not in KNOWN_SERIES.keys():
            # This is an episode from a series we haven't seem yet
            LOG.debug('Program %s is from an unknown series %s', self.programId, self.seriesId)
            Series(self.seriesId)

    def get_details(self):
        try:
            r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.programId)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            LOG.error('Could not get program details: %s', e)
            return
        self.isAvailable = json['isAvailable']
        if self.isAvailable:
            self.mediaUrl = json.get('mediaUrl', None)
            if self.mediaUrl:
                self.mediaUrl = re.sub(r'\.net/z/', '.net/i/', self.mediaUrl)
                self.mediaUrl = re.sub(r'manifest\.f4m$', 'master.m3u8', self.mediaUrl)
            self.hasSubtitles = json.get('hasSubtitles', False)
            if self.hasSubtitles:
                self.subtitleUrl = unquote(json['mediaAssets'][0]['webVttSubtitlesUrl'])
            self.duration = utils.parse_duration(json['duration'])

        # Update the self.filename
        self.make_filename()

    def make_filename(self):
        if self.seriesId:
            LOG.debug("Making filename for series %s", self.seriesId)
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

        self.filename = os.path.join(basedir, utils.valid_filename(filename))

    def __str__(self):
        if self.seriesId:
            series = KNOWN_SERIES[self.seriesId]
            season_number, episode_number = series.programIds[self.programId]
            string = '{} ({}): {} - {}'.format(
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
        LOG.info('Creating new season: %s: %s', idx, json['name'])

        self.id = json['id']
        self.name = re.sub(r'\s+', ' ', json['name'])
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
        LOG.info('Creating new series: %s', series_id)

        # Register our seriesId. The object is updated later
        KNOWN_SERIES[series_id] = self

        try:
            r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            LOG.error('Not able get details for %s: %s', series_id, e)
            sys.exit(1)

        self.seriesId = series_id
        self.title = re.sub(r'\s+', ' ', json['title'])
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
            LOG.debug('Series %s: Adding %s to S%d, E%d',
                      self.seriesId, program.title, season_index, episode_number)
            self.programIds[item['programId'].lower()] = (season_index, episode_number)
            program.make_filename()
            self.seasons[season_index].episodes.append(program)
        LOG.debug("In get_episodes, added %d episodes", len(self.programIds.keys()))

    def __str__(self):
        string = '{} : {} Sesong(er)'.format(self.title, len(self.seasons))
        return string


def search(search_string, search_type):

    if search_type not in ['series', 'program']:
        LOG.error('Unknown search type: %s', search_type)

    try:
        r = SESSION.get(NRK_TV_MOBIL_API + '/search/' + search_string)
        r.raise_for_status()
        json = r.json()
    except Exception as e:
        LOG.error('Not able to parse search-results: %s', e)
        return

    results = []
    hits = json.get('hits', [])
    if hits is None:
        hits = []
    for item in reversed(hits):
        if item['type'] == 'serie' and search_type == 'series':
            results.append(Series(item['hit']['seriesId']))
        elif item['type'] in ['program', 'episode'] and search_type == 'program':
            results.append(Program(item['hit']))
        if item['type'] not in ['serie', 'program', 'episode']:
            LOG.warning('Unknown item type: %s', item['type'])

    return results


def ask_for_program_download(programs):
    print('\nMatching programs')
    for i, p in enumerate(programs):
        print('{:2}: {}'.format(i, p))
    selection = utils.get_slice_input(len(programs))
    LOG.debug('You selected %s', selection)

    print('Getting program details for your selection of {} programs...'.format(len(programs[selection])))
    programs_to_download = []
    # TODO: It takes time to call .get_details() sequentially. Should be rewritten to use parallel workers.
    for program in programs[selection]:
        program.get_details()
        if program.isAvailable:
            programs_to_download.append(program)
            if program.seriesId:
                download_series_metadata(KNOWN_SERIES[program.seriesId])
        else:
            LOG.info('Sorry, program not available: %s', program.title)

    download_programs(programs_to_download)


def download_worker(args):
    program, program_idx, progress_list = args
    program_filename = program.filename
    download_dir = os.path.dirname(program_filename)
    image_filename = program_filename + '.jpg'
    subtitle_file = program_filename + '.no.srt'
    video_filename = program_filename + '.m4v'

    # Create directory if needed
    if not os.path.exists(download_dir):
        try:
            try:
                # Can't use exist_ok=True under Python 2.7
                # And some other thread might have created the directory just before us
                os.makedirs(download_dir)
            except OSError:
                pass
        except Exception as e:
            LOG.error('Could not create directory %s: %s', download_dir, e)
            return

    # Download image
    if not os.path.exists(image_filename):
        try:
            LOG.info('Downloading image for %s', program.title)
            urlretrieve(program.imageUrl, image_filename)
        except Exception as e:
            LOG.warning('Could not download image for program %s: %s', program.title, e)

    # Download subtitles
    if program.hasSubtitles and not os.path.exists(subtitle_file):
        LOG.info('Downloading subtitles for %s', program.title)
        cmd = ['ffmpeg', '-loglevel', '8', '-i', program.subtitleUrl, subtitle_file]
        try:
            subprocess.call(cmd, stdin=open(os.devnull, 'r'))
        except Exception as e:
            LOG.warning('Could not download subtitles for program %s: %s', program.title, e)

    # Download video
    if not os.path.exists(video_filename):
        cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', program.mediaUrl]
        if os.path.exists(subtitle_file):
            cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0', 'language=nor']
        # cmd += ['-metadata', 'description="{}"'.format(obj.description)]
        # cmd += ['-metadata', 'track="24"']
        cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', video_filename]
        try:
            LOG.info("Starting command: %s", cmd)
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdin=open(os.devnull, 'r'),
                                       universal_newlines=True)
            while process.poll() is None:
                seconds_downloaded = utils.ffmpeg_seconds_downloaded(process)
                progress_list[program_idx] = round(seconds_downloaded)
                time.sleep(0.5)
            process.wait()
        except Exception as e:
            LOG.warning('Unable to download program %s:%s : %s', program.title, program.episodeTitle, e)


def download_programs(programs):
    total_duration = datetime.timedelta()
    for program in programs:
        total_duration += program.duration
    total_duration = total_duration - datetime.timedelta(microseconds=total_duration.microseconds)
    print('Ready to download {} programs, with total duration {}'.format(len(programs), total_duration))

    # Under Python 2.7, we can't use with .. as, .. as:
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    manager = multiprocessing.Manager()

    shared_progress = manager.list([0]*len(programs))
    progress_bar = tqdm.tqdm(desc='Downloading', total=round(total_duration.total_seconds()),
                             unit='s', unit_scale=True)

    LOG.debug('Starting pool of workers')
    args = [(program, idx, shared_progress) for idx, program in enumerate(programs)]
    result = pool.map_async(download_worker, args)

    while not result.ready():
        LOG.debug('Progress: %s', shared_progress)
        time.sleep(0.1)
        progress_bar.update(sum(shared_progress) - progress_bar.n)
    progress_bar.update(progress_bar.total - progress_bar.n)
    progress_bar.close()

    LOG.debug('All workers finished. Result: %s', result.get())


def download_series_metadata(series):
    download_dir = os.path.join(nrkdownload.DOWNLOAD_DIR, series.dirName)
    image_filename = 'poster.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        LOG.info('Downloading image for series %s', series.title)
        try:
            try:
                # Can't use exist_ok = True under Python 2.7
                os.makedirs(download_dir)
            except OSError:
                pass
            urlretrieve(series.imageUrl, os.path.join(download_dir, image_filename))
        except Exception as e:
            LOG.error('Could not download metadata for series %s: %s', series.title, e)


def find_all_episodes(series):
    programs = []
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    return programs


def search_from_cmdline(args):
    if args.series:
        series = search(args.series, 'series')
        if len(series) == 1:
            print('\nOnly one matching series: {}'.format(series[0].title))
            programs = find_all_episodes(series[0])
            ask_for_program_download(programs)
        elif len(series) > 1:
            print('\nMatching series:')
            for i, s in enumerate(series):
                print('{:2}: {}'.format(i, s))
            index = utils.get_integer_input(len(series) - 1)
            programs = find_all_episodes(series[index])
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching series')
    elif args.program:
        programs = search(args.program, 'program')
        if programs:
            ask_for_program_download(programs)
        else:
            print('Sorry, no matching programs')
    else:
        LOG.error('Unknown state, not sure what to do')


def download_from_url(url):

    parsed_url = urlparse(url)

    "https://tv.nrk.no/serie/p3-sjekker-ut/MYNT12000317/sesong-1/episode-3"
    "https://tv.nrk.no/serie/paa-fylla"

    series_match = re.match(r"/serie/([\w-]+)$", parsed_url.path)
    program_match = re.match(r"/program/(\w+)", parsed_url.path)
    episode_match = re.match(r"/serie/([\w-]+)/(\w+)", parsed_url.path)
    if program_match:
        series_id = None
        program_id = program_match.group(1).lower()
    elif episode_match:
        series_id = episode_match.group(1)
        program_id = episode_match.group(2).lower()
    elif series_match:
        series_id = series_match.group(1)
        program_id = None
    else:
        LOG.error("Don't know what to do with URL: %s", url)
        sys.exit(1)

    if series_id:
        series = Series(series_id)
        download_series_metadata(series)
        if not program_id:
            episodes = [ep for season in series.seasons for ep in season.episodes]
            # TODO: As above, this should be done in parallel
            for episode in episodes:
                episode.get_details()
            download_programs(episodes)

    if program_id:
        try:
            r = SESSION.get(NRK_PS_API + '/mediaelement/' + program_id)
            r.raise_for_status()
            json = r.json()
            json['programId'] = program_id
            json['imageId'] = json['image']['id']
            program = Program(json)
            program.get_details()
        except Exception as e:
            LOG.error('Could not get program details: %s', e)
            return
        if program.isAvailable:
            download_programs([program])
        else:
            LOG.info('Sorry, program not available: %s', program.title)

    """
    https://tv.nrk.no/serie/paa-fylla
    https://tv.nrk.no/serie/trygdekontoret/MUHH48000516/sesong-12/episode-5
    https://tv.nrk.no/serie/trygdekontoret
    https://tv.nrk.no/program/KOIF42005206/the-queen
    https://tv.nrk.no/program/KOID20001217/geert-wilders-nederlands-hoeyrenasjonalist
    https://tv.nrk.no/program/KOID76002309/the-act-of-killing
    """
