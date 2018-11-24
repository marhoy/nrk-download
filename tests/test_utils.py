import nrkdownload.utils
import datetime


def test_valid_filename(string=r':blah/bl:ah.ext'):
    filename = nrkdownload.utils.valid_filename(string)
    assert filename == 'blahblah.ext'


def test_parse_duration(string='PT3H12M41.6S'):
    # PT28M39S : 28m39s
    # PT3H12M41.6S : 3h12m41.6s
    duration = nrkdownload.utils.parse_duration(string)
    assert duration == datetime.timedelta(hours=3, minutes=12, seconds=41.6)


def test_classmethod():
    c = nrkdownload.utils.ClassProperty()
    assert c
