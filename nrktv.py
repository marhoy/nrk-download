import requests
import os.path

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

session = requests.Session()
session.headers['app-version-android'] = '999'


def get_categories(api='nrk_tv_mobil'):

    if api == 'nrk_tv_mobil':
        r = session.get(NRK_TV_MOBIL_API + '/categories')
        r.raise_for_status()
        return r.json()


def search(string, api='nrk_tv_mobil'):

    if api == 'nrk_tv':
        r = session.get(NRK_TV_API + '/autocomplete?query=' + string)
    else:
        r = session.get(NRK_TV_MOBIL_API + '/search/' + string)

    r.raise_for_status()
    series = []
    programs = []

    for item in r.json()['hits']:
        if item['type'] == 'serie':
            series.append(Serie(item['hit']))
        elif item['type'] in ['program', 'episode']:
            programs.append(Program(item['hit']))

    return series, programs


class Category:
    def __init__(self, json):
        self.categoryId = json['categoryId']
        self.displayValue = json['displayValue']
        self.availableFilters = json['availableFilters']


class Program:
    def __init__(self, json):
        self.programId = json['programId']
        self.title = json['title']
        self.description = json['description']
        self.seriesTitle = ''
        self.seasonNumber = ''
        self.episodeNumberOrDate = ''
        self.s0xe0y = ''
        self.fileName = ''
        # self.get_details()

    def get_details(self):
        r = session.get(NRK_PS_API + '/mediaelement/' + self.programId)
        r.raise_for_status()
        json = r.json()

        self.seriesTitle = json['seriesTitle'] if json['seriesTitle'] != 'None' else ''
        self.seasonNumber = json['seasonNumber'] if json['seasonNumber'] != 'None' else ''
        self.episodeNumberOrDate = json['episodeNumberOrDate'] if json['seriesTitle'] != 'None' else ''

        if self.episodeNumberOrDate and self.episodeNumberOrDate.find(':') > 0:
            self.s0xe0y = 'S' + self.seasonNumber.zfill(2) + 'E' + self.episodeNumberOrDate.split(':')[0].zfill(2)
        else:
            self.s0xe0y = ''

        if self.seriesTitle and self.s0xe0y:
            self.fileName = os.path.join(self.seriesTitle, 'Season ' + self.seasonNumber.zfill(2),
                                         self.seriesTitle + ' - ' + self.s0xe0y + ' - ' + self.title)
        elif self.seriesTitle:
            self.fileName = os.path.join(self.seriesTitle, 'Season ' + self.seasonNumber.zfill(2),
                                         self.seriesTitle + ' - ' + json['episodeTitle'])
        else:
            self.fileName = os.path.join(self.title)

        image_url = 'http://m.nrk.no/m/img?kaleidoId={}&width={}'.format(json['imageId'], 640)

    def __str__(self):
        string = 'ID: {}\n'.format(self.programId)
        string += '    Title: {}\n'.format(self.title)
        string += '    Episode: {}\n'.format(self.episodeNumberOrDate)
        string += '    Filename: {}\n'.format(self.fileName)
        return string


class Serie:
    def __init__(self, json):
        self.seriesId = json['seriesId']
        self.title = json['title']
        self.description = json['description']
        self.imageID = json['imageId']

    def __str__(self):
        string = 'ID: {}\n'.format(self.seriesId)
        string += '    Title: {}'.format(self.title)
        return string

    def episodes(self):
        r = session.get(NRK_TV_MOBIL_API + '/series/' + self.seriesId)
        r.raise_for_status()

        episodes = []
        for item in r.json()['programs']:
            episodes.append(Program(item))

        return episodes


if __name__ == '__main__':
    # print('Categories:\n', get_categories())
    # print('Search:\n', search('test', api='nrk_tv_mobil'))
    series, programs = search('snøfall')

    for s in series:
        print(s)

    for p in programs:
        print(p)

    # for item in s['hits']:
    #     print(item['type'], ':')
    #     for field in item['hit']:
    #         print('\t', field, ':', item['hit'][field])
    #
    # s = episode_details('koif42002401')
    # print(s)
    # for item in s['hits']:
    #     print(item['type'], ':')
    #     for field in item['hit']:
    #         print('\t', field, ':', item['hit'][field])
    #
