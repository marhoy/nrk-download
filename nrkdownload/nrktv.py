# This is needed if we are running under Python 2.7
from __future__ import unicode_literals

import datetime
import logging
import multiprocessing
import os.path
import re
import subprocess
import sys
import time

import requests
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
from . import utils
from . import config

# Module wide logger
LOG = logging.getLogger(__name__)

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

# Initialize requests session
SESSION = requests.Session()
SESSION.headers['app-version-android'] = '999'


class Program:
    def __init__(self, title, program_id, description, image_url,
                 series_id=None, episode_number_or_date=None, episode_title=None):
        LOG.info('Creating new Program: %s : %s', title, program_id)

        self.program_id = program_id
        self.title = title
        self.description = description
        self.image_url = image_url
        self.series_id = series_id
        self.episode_number_or_date = episode_number_or_date
        self.episode_title = episode_title
        self.media_urls = None
        self.subtitle_urls = None
        self.filename = None
        self.duration = None

    def get_download_details(self, json=None):

        if json is None:
            try:
                r = SESSION.get(NRK_PS_API + '/mediaelement/' + self.program_id)
                r.raise_for_status()
                json = r.json()
            except Exception as e:
                LOG.error('Could not get program details: %s', e)
                sys.exit(1)

        is_available = json.get('isAvailable', False)
        self.duration = utils.parse_duration(json.get('duration', None))

        if is_available:
            self.media_urls = []
            self.subtitle_urls = []
            for media in json.get('mediaAssets', None):
                url = media.get('url', None)
                subtitle_url = media.get('webVttSubtitlesUrl', None)

                if url:
                    url = re.sub(r'\.net/z/', '.net/i/', url)
                    url = re.sub(r'manifest\.f4m$', 'master.m3u8', url)
                    self.media_urls.append(url)
                if subtitle_url:
                    subtitle_url = unquote(subtitle_url)
                    subtitle_url = re.sub(r'^https', 'http', subtitle_url)
                    self.subtitle_urls.append(subtitle_url)
        else:
            LOG.warning("%s is not available for download", self.title)

    def make_filename(self):
        if self.series_id:
            LOG.debug("Making filename for program %s", self.title)
            series = series_from_series_id(self.series_id)
            season_number, episode_number = series.get_program_ids()[self.program_id]
            basedir = os.path.join(config.DOWNLOAD_DIR, series.dir_name,
                                   series.seasons[season_number].dir_name)

            filename = series.title
            filename += ' - S{:02}E{:02}'.format(season_number + 1, episode_number + 1)

            if not self.title.lower().startswith(series.title.lower()):
                filename += ' - {}'.format(self.title)

            regex_match = re.match('^(\d+):(\d+)$', self.episode_number_or_date)
            if regex_match:
                filename += ' - {}of{}'.format(regex_match.group(1), regex_match.group(2))
            else:
                filename += ' - {}'.format(self.episode_number_or_date)
        else:
            basedir = config.DOWNLOAD_DIR
            filename = self.title

        self.filename = os.path.join(basedir, utils.valid_filename(filename))

    def __str__(self):
        if False:
            series = config.KNOWN_SERIES[self.series_id]
            season_number, episode_number = series.programIds[self.programId]
            string = '{} ({}): {} - {}'.format(
                series.title,
                series.seasons[season_number].name,
                self.title,
                self.episode_number_or_date)
            string += ' - S{:02}E{:02}'.format(season_number + 1, episode_number + 1)
        else:
            string = self.title
            if self.episode_number_or_date and not string.endswith(self.episode_number_or_date):
                string += ': ' + self.episode_number_or_date
        if len(string) > config.MAX_OUTPUT_STRING_LENGTH:
            string = string[:config.MAX_OUTPUT_STRING_LENGTH - 3] + '...'
        return string


class Season:
    def __init__(self, idx, season_id, name):
        LOG.info('Creating new season: %s: %s: %s', idx, season_id, name)

        self.number = idx
        self.id = season_id
        self.name = name
        self.episodes = []
        self.dir_name = utils.valid_filename('Season {:02}'.format(self.number + 1))
        if not self.name.startswith('Sesong'):
            self.dir_name = utils.valid_filename(self.dir_name + '- {}'.format(self.name))

    def __str__(self):
        string = '{}: {} ({} episoder)'.format(self.number + 1, self.name, len(self.episodes))
        return string


class Series:
    def __init__(self, series_id, title, description, season_ids, image_url, dir_name):
        LOG.info('Creating new series: %s', series_id)

        self.series_id = series_id
        self.title = title
        self.description = description
        self.image_url = image_url
        self.dir_name = dir_name
        self.season_ids = season_ids
        self.seasons = []
        self.seasonId2Idx = {}
        self.program_ids = {}

        # Update the known series with our instance
        add_to_known_series(self)

    def get_program_ids(self):
        if not self.program_ids:
            self.get_seasons_and_episodes()
        return self.program_ids

    def get_seasons_and_episodes(self, json=None):

        if json is None:
            LOG.info("Downloading detailed info on %s", self.series_id)
            try:
                r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + self.series_id)
                r.raise_for_status()
                json = r.json()
            except Exception as e:
                LOG.error('Not able get details for %s: %s', self.series_id, e)
                sys.exit(1)

        LOG.info("Adding seasons to  %s", self.series_id)
        self.seasons = []
        for idx, season in enumerate(reversed(json['seasonIds'])):
            season_name = re.sub(r'\s+', ' ', season['name'])
            season_id = season['id']
            self.seasons.append(Season(idx=idx, season_id=season_id, name=season_name))
            self.seasonId2Idx[season['id']] = idx

        LOG.info("Adding episodes to  %s", self.series_id)
        for item in reversed(json['programs']):
            season_index = self.seasonId2Idx[item['seasonId']]
            program = new_program_from_search_result(item)
            episode_number = len(self.seasons[season_index].episodes)
            LOG.debug('Series %s: Adding %s to S%d, E%d',
                      self.series_id, program.title, season_index, episode_number)
            self.program_ids[item['programId'].lower()] = (season_index, episode_number)
            self.seasons[season_index].episodes.append(program)
        LOG.debug("In get_episodes, added %d episodes", len(self.program_ids.keys()))

    def __str__(self):
        string = '{} : {} Sesong'.format(self.title, len(self.season_ids))
        if len(self.season_ids) > 1:
            string += 'er'
        return string


def new_program_from_search_result(json):
    program_id = json['programId'].lower()
    title = re.sub(r'\s+', ' ', json['title'])
    description = json['description']
    image_url = utils.create_image_url(json['imageId'])
    series_id = json.get('seriesId', None)
    episode_number_or_date = json.get('episodeNumberOrDate', None)
    episode_title = json.get('episodeTitle', None)

    program = Program(title=title, program_id=program_id, description=description, image_url=image_url,
                      series_id=series_id, episode_number_or_date=episode_number_or_date, episode_title=episode_title)
    return program


def new_series_from_search_result(json):
    series_id = json['seriesId'].lower()
    title = re.sub(r'\s+', ' ', json['title'])
    description = json['description']
    season_ids = {season['id'] for season in json['seasons']}
    image_url = utils.create_image_url(json['imageId'])
    dir_name = utils.valid_filename(title)

    series = Series(series_id=series_id, title=title, description=description, season_ids=season_ids,
                    image_url=image_url, dir_name=dir_name)
    return series


def series_from_series_id(series_id):
    if series_id in config.KNOWN_SERIES:
        return config.KNOWN_SERIES[series_id]

    LOG.info("Getting info on unkown series %s", series_id)
    r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + series_id)
    r.raise_for_status()
    json = r.json()
    json['seasons'] = json['seasonIds']

    series = new_series_from_search_result(json)
    series.get_seasons_and_episodes(json=json)
    add_to_known_series(series)
    return series


def add_to_known_series(instance):
    if instance.series_id not in config.KNOWN_SERIES:
        LOG.info("Adding unknown series to global dict: %s", instance.series_id)
        config.KNOWN_SERIES[instance.series_id] = instance


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
            results.append(new_series_from_search_result(item['hit']))
        elif item['type'] in ['program', 'episode'] and search_type == 'program':
            results.append(new_program_from_search_result(item['hit']))
        if item['type'] not in ['serie', 'program', 'episode']:
            LOG.warning('Unknown item type: %s', item['type'])

    return results


def download_worker(args):
    program, program_idx, progress_list = args
    if not program.filename:
        program.make_filename()
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
            urlretrieve(program.image_url, image_filename)
        except Exception as e:
            LOG.warning('Could not download image for program %s: %s', program.title, e)

    # Download subtitles
    if program.subtitle_urls and not os.path.exists(subtitle_file):
        LOG.info('Downloading subtitles for %s', program.title)
        cmd = ['ffmpeg', '-loglevel', '8', '-i', program.subtitle_urls[0], subtitle_file]
        try:
            subprocess.call(cmd, stdin=open(os.devnull, 'r'))
        except Exception as e:
            LOG.warning('Could not download subtitles for program %s: %s', program.title, e)

    # Download video
    if not os.path.exists(video_filename):

        # The video might be in several parts
        output_filenames = []
        downloaded_seconds = []
        for media_url_idx, media_url in enumerate(program.media_urls):
            if len(program.media_urls) > 1:
                output_filename = program_filename + '-part{}'.format(media_url_idx) + '.m4v'
            else:
                output_filename = video_filename
            downloaded_seconds.append(0)

            cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', media_url]
            if os.path.exists(subtitle_file):
                cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0', 'language=nor']
            # cmd += ['-metadata', 'description="{}"'.format(obj.description)]
            # cmd += ['-metadata', 'track="24"']
            cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', output_filename]
            try:
                LOG.debug("Starting command: %s", ' '.join(cmd))
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdin=open(os.devnull, 'r'),
                                           universal_newlines=True)
                while process.poll() is None:
                    downloaded_seconds[media_url_idx] = utils.ffmpeg_seconds_downloaded(process)
                    progress_list[program_idx] = round(sum(downloaded_seconds))
                    time.sleep(0.5)
                process.wait()
                output_filenames.append(output_filename)
            except Exception as e:
                LOG.warning('Unable to download program %s:%s : %s', program.title, program.episodeTitle, e)

        # If the program was divided in parts, we need to concatenate them
        if len(output_filenames) > 1:
            LOG.info("Concatenating the %d parts of %s", len(output_filenames), program.title)
            with open(program_filename + '-parts.txt', "w") as file:
                for output_filename in output_filenames:
                    file.write("file '" + output_filename + "'\n")
            cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', program_filename + '-parts.txt']
            cmd += ['-c', 'copy', video_filename]
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdin=open(os.devnull, 'r'), universal_newlines=True)
            process.wait()

            # Remove the temporary file list and the -part files
            os.remove(program_filename + '-parts.txt')
            for file in output_filenames:
                os.remove(file)


def download_programs(programs):
    total_duration = datetime.timedelta()
    for program in programs:
        total_duration += program.duration
    total_duration = total_duration - datetime.timedelta(microseconds=total_duration.microseconds)
    print('Ready to download {} programs, with total duration {}'.format(len(programs), total_duration))


def download_programs_in_parallel(programs):
    total_duration = datetime.timedelta()
    for program in programs:
        if program.duration is None:
            program.get_download_details()
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
    download_dir = os.path.join(config.DOWNLOAD_DIR, series.dir_name)
    image_filename = 'poster.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        LOG.info('Downloading image for series %s', series.title)
        try:
            try:
                # Can't use exist_ok = True under Python 2.7
                os.makedirs(download_dir)
            except OSError:
                pass
            urlretrieve(series.image_url, os.path.join(download_dir, image_filename))
        except Exception as e:
            LOG.error('Could not download metadata for series %s: %s', series.title, e)


def find_all_episodes(series):
    programs = []
    series.get_seasons_and_episodes()
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    return programs


def download_from_url(url):

    parsed_url = urlparse(url)

    "https://tv.nrk.no/serie/p3-sjekker-ut/MYNT12000317/sesong-1/episode-3"
    "https://tv.nrk.no/serie/paa-fylla"

    # TODO: Format for episode URL have changed

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

    if program_id:
        try:
            r = SESSION.get(NRK_PS_API + '/mediaelement/' + program_id)
            r.raise_for_status()
            json = r.json()
            json['programId'] = program_id
            json['imageId'] = json['image']['id']
            program = new_program_from_search_result(json)
            program.get_download_details(json=json)
        except Exception as e:
            LOG.error('Could not get program details: %s', e)
            return

        if program.media_urls:
            download_programs_in_parallel([program])
        else:
            LOG.info('Sorry, program not available: %s', program.title)

        if program.series_id:
            series_id = program.series_id

    elif series_id:
        series = series_from_series_id(series_id)
        download_series_metadata(series)
        series.get_seasons_and_episodes()
        episodes = [ep for season in series.seasons for ep in season.episodes]
        download_programs_in_parallel(episodes)


    """
    https://tv.nrk.no/serie/paa-fylla
    https://tv.nrk.no/serie/trygdekontoret/MUHH48000516/sesong-12/episode-5
    https://tv.nrk.no/serie/trygdekontoret
    https://tv.nrk.no/program/KOIF42005206/the-queen
    https://tv.nrk.no/program/KOID20001217/geert-wilders-nederlands-hoeyrenasjonalist
    https://tv.nrk.no/program/KOID76002309/the-act-of-killing
    """
