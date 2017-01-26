import re
import sys
import datetime

from . import LOG, nrktv


def series_download(series):
    programs = []
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    nrktv.ask_for_program_download(programs)


def search_from_cmdline(args):
    if args.series:
        series = nrktv.search(args.search_string, 'series')
        if len(series) == 1:
            print('\nOnly one matching series')
            series_download(series[0])
        elif len(series) > 1:
            print('\nMatching series:')
            for i, s in enumerate(series):
                print('{:2}: {}'.format(i, s))
            index = get_integer_input(len(series) - 1)
            series_download(series[index])
        else:
            print('Sorry, no matching series')
    elif args.program:
        programs = nrktv.search(args.search_string, 'program')
        if programs:
            nrktv.ask_for_program_download(programs)
        else:
            print('Sorry, no matching programs')
    else:
        LOG.error('Unknown state, not sure what to do')


def valid_filename(string):
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


def get_image_url(image_id):
    return 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(image_id, 960)


def parse_duration(string):
    # PT28M39S : 28m39s
    # PT3H12M41.6S : 3h12m41.6s
    hours = minutes = seconds = 0
    hours_search = re.search('(\d+)H', string)
    minutes_search = re.search('(\d+)M', string)
    seconds_search = re.search('([\d.]+)S', string)
    if hours_search:
        hours = int(hours_search.group(1))
    if minutes_search:
        minutes = int(minutes_search.group(1))
    if seconds_search:
        seconds = float(seconds_search.group(1))

    try:
        duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except Exception as e:
        LOG.warning('Unable to calculate duration: {}: {}'.format(string, e))
        return datetime.timedelta()

    return duration


def ffmpeg_seconds_downloaded(process):
    downloaded_time = datetime.timedelta()

    line = process.stderr.readline()
    if line:
        time_match = re.search('.+\s+time=([\d:.]+)', line)
        if time_match:
            downloaded_time_list = time_match.group(1).split(':')
            downloaded_time = datetime.timedelta(hours=int(downloaded_time_list[0]),
                                                 minutes=int(downloaded_time_list[1]),
                                                 seconds=float(downloaded_time_list[2]))

        # rate_match = re.search('\s+bitrate=([\d.]+)', line)
        # if rate_match:
        #    download_rate = rate_match.group(1)

    return downloaded_time.total_seconds()
