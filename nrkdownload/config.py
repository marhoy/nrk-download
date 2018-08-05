import os

# This is where the downloaded files end up
DOWNLOAD_DIR = os.getenv('NRKDOWNLOAD_DIR', os.path.expanduser('~/Downloads/nrkdownload'))

# This keeps track of the series we have seen
KNOWN_SERIES = {}


def add_to_known_series(instance):
    if instance.series_id not in KNOWN_SERIES:
        KNOWN_SERIES[instance.series_id] = instance
