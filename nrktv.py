import requests
import os.path

NRK_TV_API = 'https://tv.nrk.no'
NRK_TV_MOBIL_API = 'https://tvapi.nrk.no/v1'
NRK_PS_API = 'http://v8.psapi.nrk.no'

session = requests.Session()
session.headers['app-version-android'] = '999'


def search(string):
    r = session.get(NRK_TV_MOBIL_API + '/search/' + string)
    r.raise_for_status()

    series = []
    programs = []
    for item in r.json()['hits']:
        if item['type'] == 'serie':
            series.append(Series(item['hit']))
        elif item['type'] in ['program', 'episode']:
            programs.append(Program(item['hit']))
    return series, programs


class Season:
    def __init__(self, json, i):
        self.id = json['id']
        self.name = json['name']
        self.number = i

    def __str__(self):
        string = '{}: {} ({})'.format(self.number, self.name, self.id)
        return string


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


class Series:
    def __init__(self, json):
        self.seriesId = json['seriesId']
        self.title = json['title']
        self.description = json['description']
        self.imageID = json['imageId']
        self.seasons = []

        r = session.get(NRK_TV_MOBIL_API + '/series/' + self.seriesId)
        r.raise_for_status()
        self.json = r.js    on()
        print(self.json)
        for i, s in enumerate(reversed(self.json['seasonIds']), start=1):
            season = Season(s, i)
            self.seasons.append(season)

    def __str__(self):
        string = 'SeriesID: {}\n'.format(self.seriesId)
        string += '    Title: {}\n'.format(self.title)
        string += '    Seasons: '
        string += '{}'.format([season.__str__() for season in self.seasons])
        return string

    def episodes(self):
        r = session.get(NRK_TV_MOBIL_API + '/series/' + self.seriesId)
        r.raise_for_status()

        episodes = []
        for item in r.json()['programs']:
            episodes.append(Program(item))
        return episodes


if __name__ == '__main__':
    series, programs = search('skam')

    for s in series:
        print(s)

    # for p in programs:
    #    print(p)
