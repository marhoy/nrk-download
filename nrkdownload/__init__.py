import subprocess
import os
import sys
import logging

from . import tv

__all__ = [tv]


# Before we continue, make sure that ffmpeg is available
try:
    subprocess.call(['ffmpeg', '-version'], stdout=open(os.devnull, 'w'))
except OSError as exception:
    print('\nFFmpeg is not installed (or not in PATH):\n  ', exception, '\n')
    print('Please install FFmpeg from https://ffmpeg.org/')
    print('See README on https://github.com/marhoy/nrk-download if you need hints.\n')
    sys.exit(1)

# Set up package-wide logging configuration
logging.basicConfig(format='[%(levelname)s] %(name)s(%(lineno)s): %(message)s',
                    level=logging.WARNING)
