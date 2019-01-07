import os


# What is the maximum string length in the list output when searching?
MAX_OUTPUT_STRING_LENGTH = 70

# This is where the downloaded files end up, unless otherwise spcified
DEFAULT_DOWNLOAD_DIR = os.getenv('NRKDOWNLOAD_DIR',
                                 os.path.expanduser('~/Downloads/nrkdownload'))
