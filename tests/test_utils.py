# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import nrkdownload.utils as utils


def test_parse_duration():

    duration = utils.parse_duration("PT3H12M41.6S")
    assert duration == datetime.timedelta(hours=3, minutes=12, seconds=41.6)


def test_ffmpeg_seconds_downloaded():

    import io

    # "ffmpeg -loglevel 8 -stats -i http://nordond35c-f.akamaihd.net/i/wo/open/34/34ca537128bcd492083545f5693fbecc75e8be55/34ca537128bcd492083545f5693fbecc75e8be55_,141,316,563,1266,2250,.mp4.csmil/master.m3u8 -c:v copy -c:a copy -bsf:a aac_adtstoasc /Users/marhoy/Downloads/nrkdownload/Pompel og pilt - Reparatørene kommer/Season 01/Pompel og pilt - Reparatørene kommer - S01E01 - Reparatørene kommer - 1of5.m4v"

    # Fake an object that could have contained the stderr stread from ffmpeg
    ffmpeg_stderr = "frame= 5116 fps=468 q=-1.0 Lsize=    7873kB time=00:03:33.33 bitrate= 302.3kbits/s speed=19.5x"

    class Process:
        pass

    process = Process()
    process.stderr = io.StringIO(ffmpeg_stderr)

    duration = utils.ffmpeg_seconds_downloaded(process)
    assert duration == datetime.timedelta(minutes=3, seconds=33.33).total_seconds()
