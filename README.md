# nrkdownload

This is yet another tool to download program and series from NRK.
It is inspired by the already existing tools. The code is written in order to be as readable as possible.

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