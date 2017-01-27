# nrkdownload

This is yet another commandline tool to download programs and series from NRK. It is inspired by the already existing tools that you can find on GitHub. The reason I decided to make yet another tool, was that I found the source code of some of the other tools to be difficult to read and understand, and thus difficult to contribute to.

## What is different?
When you download a program with this tool, it doesn't just download that file. If the program is part of a series, a directory for that series and season is created. And the file is automatically named according to its episode and season number. Subtitles and additional images are also automatically downloaded. The subtitles are also included in the .m4v-file, so you could decide to delete the .srt-file. (I have found that in some tools (like VLC), the support for included subtitles is not perfect. That's why the .srt-file is there.)

The idea behind this is that the downloaded programs should be integrate seamlessly into you favorite media server, e.g. [Plex](http://www.plex.tv).


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
You need an installation of Python 3. If you haven't already got that, download the latest version for your operating system from [python.org](https://www.python.org). You could also consider using the [Anaconda](https://www.continuum.io/downloads) Python distribution. It can be installed without root (Administrator) privileges, and contains a lot of useful packages. 

In addition to the standard packages that are typically distributed with Python, you need:
 - [requests](http://docs.python-requests.org/en/master/) (used for connecting to nrk.no and downloading program information)
 - [tqdm](https://pypi.python.org/pypi/tqdm) (used to create a progress bar when downloading video)

If you are using the Anaconda Python distribution, these packages can be installed with: `conda install requests tqdm` Otherwise, they can be installed with `pip install requests tqdm`
 
### FFmpeg
The videos and subtitles are downloaded using [FFmpeg](https://ffmpeg.org/). It is available for all major operating systems.
