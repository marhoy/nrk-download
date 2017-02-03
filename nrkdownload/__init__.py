from .constants import LOG, DOWNLOAD_DIR
from .nrktv import search_from_cmdline

import subprocess
import os
import sys

# Before we continue, make sure that ffmpeg is available
try:
    subprocess.call(['ffmpeg', '-version'], stdout=open(os.devnull, 'w'))
except OSError as e:
    print('\nFFmpeg is not installed (or not in PATH):\n  ', e, '\n')
    print('Please install FFmpeg from https://ffmpeg.org/')
    print('See README on https://github.com/marhoy/nrk-download if you need hints.\n')
    sys.exit(1)
