import logging
import os

# Package-wide logging configuration
logging.basicConfig(format='{levelname}: {message}', level=logging.WARNING, style='{')
LOG = logging.getLogger()

# This is where the files end up
DOWNLOAD_DIR = os.getenv('NRKDOWNLOAD_DIR', os.path.expanduser('~/Downloads/nrkdownload'))
