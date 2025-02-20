"""Package initialization."""

import importlib.metadata
import sys

from ffmpeg import FFmpeg

__all__ = ["__version__"]
__version__ = importlib.metadata.version(__package__) if __package__ else "unknown"

try:
    ffmpeg_version = FFmpeg().option("version").execute().decode("utf-8")
except FileNotFoundError:
    print(
        "\nFFmpeg not found, must be installed to use this package.\n"
        "See documentation: https://nrkdownload.readthedocs.io/"
    )
    sys.exit(1)
