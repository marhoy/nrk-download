# nrkdownload

This is yet another tool to download program and series from NRK.
It is inspired by the already existing tools. The code is written in Python, and order to be as readable as possible.

## What is different?
When programs and series are downloaded, a directory hierarchy is created for each series and season.
Subtitles and images for programs/episodes and series are automatically downloaded.
The idea is that the subdirectory should integrate seamless into e.g. [Plex](http://www.plex.tv).


```
SKAM
├── poster.jpg
├── Season 01 - Sesong 1
│   ├── SKAM - S01E01 - 1of11.jpg
│   ├── SKAM - S01E01 - 1of11.m4v
│   ├── SKAM - S01E01 - 1of11.no.srt
⋮
├── Season 02 - Sesong 2
│   ├── SKAM - S02E01 - 1of12.jpg
│   ├── SKAM - S02E01 - 1of12.m4v
│   ├── SKAM - S02E01 - 1of12.no.srt
⋮
└── Season 03 - Sesong 3
    ├── SKAM - S03E01 - 1of10.jpg
    ├── SKAM - S03E01 - 1of10.m4v
    ├── SKAM - S03E01 - 1of10.no.srt
    ⋮
    ├── SKAM - S03E10 - 10of10.jpg
    ├── SKAM - S03E10 - 10of10.m4v
    └── SKAM - S03E10 - 10of10.no.srt
```

## Requirements and installation
### Python and packages
You need an installation of Python 3. If you haven't already got that, download the latest version for your 
operating system from [python.org](https://www.python.org).
You could also consider using the [Anaconda](https://www.continuum.io/downloads) Python distribution. It can
be installed without root (Administrator) privileges, and contains a lot of useful packages. 

In addition to the standard packages that are typically distributed with Python, you need:
 - [requests](http://docs.python-requests.org/en/master/) (used for connecting to nrk.no and downloading program information)
 - [tqdm](https://pypi.python.org/pypi/tqdm) (used to create a progress bar when downloading video)

If you are using the Anaconda Python distribution, these packages can be installed with:
`conda install requests tqdm`
Otherwise, they can be installed with
`pip install requests tqdm`
 
### FFmpeg
The videos and subtitles are downloaded using [FFpeg](https://ffmpeg.org/).
