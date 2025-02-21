# Features

The `nrkdownload` tool enables downloading of TV series and programs from NRK. It can
download a single program or episode, a season of a series, or a whole series.

## Organization of media and metadata

The idea behind the tool is that the downloaded programs should integrate seamlessly
into you favorite media server, e.g. Plex. If you for example download all the episodes
of the popular series
[Førstegangstjenesten](https://tv.nrk.no/serie/foerstegangstjenesten), you would get a
directory-structure like this:

```{ .text .no-copy}
Førstegangstjenesten
├── banner.jpg
├── Season 01
│   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.jpg
│   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.m4v
│   ├── Førstegangstjenesten - s01e01 - 1. Pilot - del 1.no.srt
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
```
