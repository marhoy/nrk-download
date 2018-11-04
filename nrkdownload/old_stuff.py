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


class Series:
    def get_episodes(self, json=None):

        if json is None:
            LOG.info("Downloading detailed info on %s", self.series_id)
            try:
                r = SESSION.get(NRK_TV_MOBIL_API + '/series/' + self.series_id)
                r.raise_for_status()
                json = r.json()
            except Exception as e:
                LOG.error('Not able get details for %s: %s', self.series_id, e)
                sys.exit(1)

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


class Program:
    def get_download_details(self, json=None):
        """
        This method sets the media_urls and subtitle_urls properties of the program object.
        When the search API was available, this information was not available from the search
        results, so we had to get that information later.

        :param json: information about the element id
        :return:
        """
        if json is None:
            try:
                json = nrkapi.get_mediaelement(self.program_id)
            except Exception as e:
                LOG.error('Could not get program details: %s', e)
                raise e

        is_available = json.get('isAvailable', False)
        self.duration = utils.parse_duration(json.get('duration', None))

        if is_available:
            self.media_urls = json.get('media_urls', [])
            self.subtitle_urls = json.get('subtitle_urls', [])
        else:
            LOG.warning("%s is not available for download", self.title)

    @property
    def filename(self):
        """
        This method either returns an already created filename, or it creates a new one.

        :return: filename: str
        """
        if self._filename:
            return self._filename

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

        self._filename = os.path.join(basedir, utils.valid_filename(filename))
        return self._filename

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


def add_to_known_series(instance):
    if instance.series_id not in config.KNOWN_SERIES:
        LOG.info("Adding unknown series to global dict: %s", instance.series_id)
        config.KNOWN_SERIES[instance.series_id] = instance


def find_all_episodes(series):
    programs = []
    series.get_seasons_and_episodes()
    for season in series.seasons:
        for episode in season.episodes:
            programs.append(episode)
    return programs


# def download_from_url(url):
#
#     parsed_url = urlparse(url)
#
#     "https://tv.nrk.no/serie/p3-sjekker-ut/MYNT12000317/sesong-1/episode-3"
#     "https://tv.nrk.no/serie/paa-fylla"
#
#     # TODO: Format for episode URL have changed
#
#     series_match = re.match(r"/serie/([\w-]+)$", parsed_url.path)
#     program_match = re.match(r"/program/(\w+)", parsed_url.path)
#     episode_match = re.match(r"/serie/([\w-]+)/(\w+)", parsed_url.path)
#
#     if program_match:
#         series_id = None
#         program_id = program_match.group(1).lower()
#     elif episode_match:
#         series_id = episode_match.group(1)
#         program_id = episode_match.group(2).lower()
#     elif series_match:
#         series_id = series_match.group(1)
#         program_id = None
#     else:
#         LOG.error("Don't know what to do with URL: %s", url)
#         sys.exit(1)
#
#     if program_id:
#         try:
#             r = SESSION.get(NRK_PS_API + '/mediaelement/' + program_id)
#             r.raise_for_status()
#             json = r.json()
#             json['programId'] = program_id
#             json['imageId'] = json['image']['id']
#             program = new_program_from_search_result(json)
#             program.get_download_details(json=json)
#         except Exception as e:
#             LOG.error('Could not get program details: %s', e)
#             return
#
#         if program.media_urls:
#             download_programs([program])
#         else:
#             LOG.info('Sorry, program not available: %s', program.title)
#
#         if program.series_id:
#             series_id = program.series_id
#
#     elif series_id:
#         series = series_from_series_id(series_id)
#         download_series_metadata(series)
#         series.get_seasons_and_episodes()
#         episodes = [ep for season in series.seasons for ep in season.episodes]
#         download_programs(episodes)
#
#
#     """
#     https://tv.nrk.no/serie/paa-fylla
#     https://tv.nrk.no/serie/trygdekontoret/MUHH48000516/sesong-12/episode-5
#     https://tv.nrk.no/serie/trygdekontoret
#     https://tv.nrk.no/program/KOIF42005206/the-queen
#     https://tv.nrk.no/program/KOID20001217/geert-wilders-nederlands-hoeyrenasjonalist
#     https://tv.nrk.no/program/KOID76002309/the-act-of-killing
#     """
