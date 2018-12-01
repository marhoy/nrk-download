Features
========

This is a commandline tool to download content from NRK
(Norwegian public broadcaster). It supports downloading TV, radio and podcasts.
The tool is written in Python, and is compatible with Python 2.7
and 3.x. It has been tested under Linux, Mac OS X and Windows.

As of autumn 2018, NRK has started to require a secret key in the header of
the API requests. This download-tool works even after those restrictions.
Users outside of Norway should note that some of the content is
geo-restricted.


How is this tools different than others?
----------------------------------------

When you download a program with this tool, it doesn't just download one
file. If the program is part of a series, directories for the series and
season is created. And the file is automatically named according to its
episode and season number. Subtitles and additional images are also
automatically downloaded. The subtitles are automatically embedded in the
.m4v-file, so you could decide to delete the .srt-file. (I have found that in
some tools (like VLC), the support for included subtitles is not perfect.
That's why the separate .srt-file is also there.)

The idea behind all of this is that the downloaded programs should integrate
seamlessly into you favorite media server, e.g. Plex. If you for example
download all the episodes of the popular series SKAM, you would get a
directory-structure like this::

    SKAM
    ├── poster.jpg
    ├── Season 01
    │   ├── SKAM - S01E01 - 1of11.jpg
    │   ├── SKAM - S01E01 - 1of11.m4v
    │   ├── SKAM - S01E01 - 1of11.no.srt
    ⋮
    ├── Season 02
    │   ├── SKAM - S02E01 - 1of12.jpg
    │   ├── SKAM - S02E01 - 1of12.m4v
    │   ├── SKAM - S02E01 - 1of12.no.srt
    ⋮
    └── Season 03
        ├── SKAM - S03E01 - 1of10.jpg
        ├── SKAM - S03E01 - 1of10.m4v
        ├── SKAM - S03E01 - 1of10.no.srt
        ⋮
        ├── SKAM - S03E10 - 10of10.jpg
        ├── SKAM - S03E10 - 10of10.m4v
        └── SKAM - S03E10 - 10of10.no.srt

