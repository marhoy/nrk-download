import logging
import os

# Package-wide logging configuration
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
LOG = logging.getLogger()

# This is where the files end up
DOWNLOAD_DIR = os.getenv('NRKDOWNLOAD_DIR', os.path.expanduser('~/Downloads/nrkdownload'))
