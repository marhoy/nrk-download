import datetime
import logging
import multiprocessing
import os.path
import subprocess
import time

import requests
import tqdm

from . import tv

try:
    # Python 3
    from urllib.request import urlretrieve
except ImportError:                 # pragma: no cover
    # Python 2
    from urllib import urlretrieve

from . import utils
from . import config


# Module wide logger
LOG = logging.getLogger(__name__)


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
            LOG.warning('Could not download subtitles for program %s: %s',
                        program.title, e)

    # Download video
    if not os.path.exists(video_filename):

        # The video might be in several parts
        output_filenames = []
        downloaded_seconds = []
        for media_url_idx, media_url in enumerate(program.media_urls):
            if len(program.media_urls) > 1:
                output_filename = program_filename + \
                                  '-part{}'.format(media_url_idx) + '.m4v'
            else:
                output_filename = video_filename
            downloaded_seconds.append(0)

            cmd = ['ffmpeg', '-loglevel', '8', '-stats', '-i', media_url]
            if os.path.exists(subtitle_file):
                cmd += ['-i', subtitle_file, '-c:s', 'mov_text', '-metadata:s:s:0',
                        'language=nor']
            # cmd += ['-metadata', 'description="{}"'.format(obj.description)]
            # cmd += ['-metadata', 'track="24"']
            cmd += ['-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc',
                    output_filename]
            try:
                LOG.debug("Starting command: %s", ' '.join(cmd))
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                           stdin=open(os.devnull, 'r'),
                                           universal_newlines=True)
                while process.poll() is None:
                    downloaded_seconds[media_url_idx] = utils.ffmpeg_seconds_downloaded(process)
                    progress_list[program_idx] = round(sum(downloaded_seconds))
                    time.sleep(1)
                process.wait()
                output_filenames.append(output_filename)
            except Exception as e:
                LOG.warning('Unable to download program %s:%s : %s',
                            program.title, program.episodeTitle, e)

        # If the program was divided in parts, we need to concatenate them
        if len(output_filenames) > 1:
            LOG.info("Concatenating the %d parts of %s",
                     len(output_filenames), program.title)
            with open(program_filename + '-parts.txt', "w") as file:
                for output_filename in output_filenames:
                    file.write("file '" + output_filename + "'\n")
            cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i',
                   program_filename + '-parts.txt']
            cmd += ['-c', 'copy', video_filename]
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                       stdin=open(os.devnull, 'r'),
                                       universal_newlines=True)
            process.wait()

            # Remove the temporary file list and the -part files
            os.remove(program_filename + '-parts.txt')
            for file in output_filenames:
                os.remove(file)

    LOG.debug("Finished downloading %s", program)


def download_programs(programs):

    for program in programs:
        if program.series_id:
            series = tv.series_from_series_id(program.series_id)
            download_series_metadata(series)

    total_duration = datetime.timedelta()
    for program in programs:
        total_duration += program.duration
    total_duration = total_duration - datetime.timedelta(microseconds=total_duration.microseconds)
    print('Ready to download {} programs, with total duration {}'.format(
        len(programs), total_duration))

    # Under Python 2.7, we can't use with .. as, .. as:
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    manager = multiprocessing.Manager()

    shared_progress = manager.list([0]*len(programs))
    progress_bar = tqdm.tqdm(desc='Downloading',
                             total=round(total_duration.total_seconds()),
                             unit='s', unit_scale=True)

    LOG.debug('Starting pool of workers')
    args = [(program, idx, shared_progress) for idx, program in enumerate(programs)]
    result = pool.map_async(download_worker, args)

    while not result.ready():
        time.sleep(1)
        LOG.debug('Progress: %s', shared_progress)
        LOG.debug("Sum downloaded: %d, pbar.n: %d", sum(shared_progress), progress_bar.n)
        progress_bar.update(sum(shared_progress) - progress_bar.n)
    progress_bar.update(progress_bar.total - progress_bar.n)
    progress_bar.close()

    LOG.debug('All workers finished. Result: %s', result.get())


def download_series_metadata(series):
    download_dir = os.path.join(config.DOWNLOAD_DIR, series.dir_name)
    image_filename = 'poster.jpg'
    if not os.path.exists(os.path.join(download_dir, image_filename)):
        LOG.info('Downloading image for series %s', series.title)
        create_directory(download_dir)
        urlretrieve(series.image_url, os.path.join(download_dir, image_filename))


def download_podcasts(episodes):
    LOG.debug("Getting ready to download %d podcasts", len(episodes))

    chunk_size = 1024

    download_dir = os.path.dirname(episodes[0].filename)
    create_directory(download_dir)
    download_series_metadata(episodes[0].podcast)

    for i, episode in enumerate(episodes):
        audio_filename = episode.filename + ".mp3"

        LOG.debug("Starting download of podcast episode %d", i + 1)
        r = requests.get(episode.media_urls[0], stream=True)
        progress_bar = tqdm.tqdm(total=int(r.headers['Content-Length']),
                                 desc='Podcast {} of {}'.format(i + 1, len(episodes)),
                                 unit='b', unit_scale=True)

        with open(audio_filename, "wb") as file:
            for data in r.iter_content(chunk_size=chunk_size):
                file.write(data)
                progress_bar.update(chunk_size)
            progress_bar.close()


def create_directory(directory):
    # Create directory if needed
    if not os.path.exists(directory):
        try:
            try:
                # Can't use exist_ok=True under Python 2.7
                # And some other thread might have created the directory just before us
                os.makedirs(directory)
            except OSError:
                pass
        except Exception as e:
            LOG.error('Could not create directory %s: %s', directory, e)
            return
