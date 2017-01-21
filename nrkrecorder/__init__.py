from .utils import get_integer_input, get_slice_input
from .nrktv import search_from_cmdline

import logging
import os

# Package-wide logging configuration
logging.basicConfig(format='{levelname}: {message}', level=logging.INFO, style='{')
LOG = logging.getLogger()

# This is where the files end up
DOWNLOAD_DIR = os.path.expanduser('~/Downloads/nrktv')
