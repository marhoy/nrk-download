from .utils import get_integer_input, get_slice_input
from .nrktv import search, ask_for_program_download

import logging
import os

# Package-wide logging configuration
logging.basicConfig(format='{levelname}: {message}', level=logging.INFO, style='{')
LOG = logging.getLogger()

# This is where the files end up
DOWNLOAD_DIR = os.path.expanduser('~/Downloads/nrktv')
