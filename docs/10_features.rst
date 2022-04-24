Features
========

This is a commandline tool for downloading content from NRK (Norwegian public
broadcaster). It supports downloading TV series and programs. The tool is written in
Python, and is compatible with Python 3.8 or newer. It has been tested under Linux, Mac
OS X and Windows.

Please only use this tool for personal purposes. You are responsible for not breaking
any Intellectual Property Rights. Users outside of Norway should note that some of the
content is geo-restricted.


Downloading media and metadata
------------------------------

The idea behind the tool is that the downloaded programs should integrate seamlessly
into you favorite media server, e.g. Plex. If you for example download all the episodes
of the popular series SKAM, you would get a directory-structure like this::

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

