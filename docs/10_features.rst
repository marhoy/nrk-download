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
of the popular series Førstegangstjenesten, you would get a directory-structure like
this::

    Førstegangstjenesten
    ├── banner.jpg
    ├── Season 01
    │   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.jpg
    │   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.m4v
    │   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.no.srt
    ⋮
    └── Season 02
        ├── Førstegangstjenesten - s02e01 - 1. episode.jpg
        ├── Førstegangstjenesten - s02e01 - 1. episode.m4v
        ├── Førstegangstjenesten - s02e01 - 1. episode.no.srt
        ⋮
        ├── Førstegangstjenesten - s02e08 - 8. episode.jpg
        ├── Førstegangstjenesten - s02e08 - 8. episode.m4v
        ├── Førstegangstjenesten - s02e08 - 8. episode.no.srt
        └── Season02.jpg

