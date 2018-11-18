import os

# This is where the downloaded files end up
DOWNLOAD_DIR = os.getenv('NRKDOWNLOAD_DIR', os.path.expanduser('~/Downloads/nrkdownload'))

# This keeps track of the series we have seen
# KNOWN_SERIES = {}

# What is the maximum string length in the list output when searching?
MAX_OUTPUT_STRING_LENGTH = 70

# API cache is disable by default
ENABLE_CACHE = False
