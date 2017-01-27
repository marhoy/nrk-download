# nrkdownload

This is yet another commandline tool to download programs and series from NRK. It is inspired by the already existing tools that you can find on GitHub. The reason I decided to make yet another tool, was that I found the source code of some of the other tools to be difficult to read and understand, and thus difficult to contribute to.

## What is different?
When you download a program with this tool, it doesn't just download that file. If the program is part of a series, a directory for that series and season is created. And the file is automatically named according to its episode and season number. Subtitles and additional images are also automatically downloaded. The subtitles are also included in the .m4v-file, so you could decide to delete the .srt-file. (I have found that in some tools (like VLC), the support for included subtitles is not perfect. That's why the .srt-file is also there.)

The idea behind this is that the downloaded programs should integrate seamlessly into you favorite media server, e.g. [Plex](http://www.plex.tv). If you for example download all the episodes of the very popular series SKAM, you would get a directory-structure like this: 

```
SKAM
├── poster.jpg
├── Season 01
│   ├── SKAM - S01E01 - 1of11.jpg
│   ├── SKAM - S01E01 - 1of11.m4v
│   ├── SKAM - S01E01 - 1of11.no.srt
⋮
├── Season 02
│   ├── SKAM - S02E01 - 1of12.jpg
│   ├── SKAM - S02E01 - 1of12.m4v
│   ├── SKAM - S02E01 - 1of12.no.srt
⋮
└── Season 03
    ├── SKAM - S03E01 - 1of10.jpg
    ├── SKAM - S03E01 - 1of10.m4v
    ├── SKAM - S03E01 - 1of10.no.srt
    ⋮
    ├── SKAM - S03E10 - 10of10.jpg
    ├── SKAM - S03E10 - 10of10.m4v
    └── SKAM - S03E10 - 10of10.no.srt
```

## Usage
In order to download something, you first have to search for it. And you have to specify whether you are searching for a particular program, or if you are searching for a series.

### Searching for a series
Let's say you are interested in downloading all the available episodes about the rescue boat "Elias". You would then use the flag `-s` to specify that you are searching for a series with the name Elias. If there is more than one matching series, you will be asked to specify which one of them you want. You respond to this by typing an integer and pressing Enter.

Then, all of the registered episodes will be listed (due to copyright-issues, some of them might not be available). You then will be asked to specify what episodes you want to download. You respond to this by typing an integer or a range. The range can be specified in different ways:
- `5-10` or `5:10`, means all episodes from 5 to 10, including both 5 and 10.
- `-10` or `:10`, means all episodes from the start (0) to 10, including 0 and 10.
- `10-` or `10:`, means all episodes from 10 to the last, including both 10 and the last.
- `-` or `:`, means all available episodes.
```
$ nrkdownload.py -s elias

Matching series:
 0: Elias på eventyr : 1 Sesong(er)
 1: Elias : 2 Sesong(er)

Enter a number in the range 0-1. (q to quit): 1

Matching programs
 0: Elias (Sesong 1): Elias - 1:26 - S01E01
 1: Elias (Sesong 1): Elias - 2:26 - S01E02
⋮
50: Elias (Sesong 2): Elias - 25:26 - S02E25
51: Elias (Sesong 2): Elias - 26:26 - S02E26

Enter a number or interval (e.g. 8 or 5-10). (q to quit): 0-10
```

## Requirements and installation
### Python and packages
You need an installation of Python 3. If you haven't already got that, download the latest version for your operating system from [python.org](https://www.python.org). You could also consider using the [Anaconda](https://www.continuum.io/downloads) Python distribution. It can be installed without root (Administrator) privileges, and contains a lot of useful packages. 

In addition to the standard packages that are typically distributed with Python, you need:
 - [requests](http://docs.python-requests.org/en/master/) (used for connecting to nrk.no and downloading program information)
 - [tqdm](https://pypi.python.org/pypi/tqdm) (used to create a progress bar when downloading video)

If you are using the Anaconda Python distribution, these packages can be installed with: `conda install requests tqdm` Otherwise, they can be installed with `pip install requests tqdm`
 
### FFmpeg
The videos and subtitles are downloaded using [FFmpeg](https://ffmpeg.org/). It is available for all major operating systems.
