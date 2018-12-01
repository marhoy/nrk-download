Examples
========

Dowloading series
-----------------

Let's say you are interested in downloading all the available episodes about
the rescue boat "Elias". You would then search for "Elias" on https://tv.nrk.no
and end up at a page with the URL https://tv.nrk.no/serie/elias. This is the
URL you want to give as argument to ``nrkdownload``::

    $ nrkdownload https://tv.nrk.no/serie/elias
    Not available for download: Elias - Elias: 1:26
    Not available for download: Elias - Elias: 2:26
    ⋮
    Not available for download: Elias - Sesong 2 - Elias: 26:26

    Matching programs
     0: Elias - Elias: 10:26
     1: Elias - Elias: 11:26
     2: Elias - Elias: 12:26
     3: Elias - Elias: 13:26
     4: Elias - Elias: 14:26
     5: Elias - Elias: 15:26
     6: Elias - Elias: 16:26
     7: Elias - Elias: 17:26
     8: Elias - Elias: 18:26

    Enter a number or Python-style interval (e.g. 8 or -2: or : ). (q to quit):


All of the registered episodes will be listed, numbered from 0.
Due to copyright-issues, some of the episodes might not be available for
download. You are then asked to specify what episodes you want to
download. You respond to this by typing an integer or a Python-style range.
Some examples:

``4``
    means the fourth episode.
``:10``
    means the 10 first episodes from 0 to 9.
``5:10``
    means the five episodes from 5 to 9.
``10:``
    means all episodes from 10 to the last, including both 10 and the last.
``:``
    means all available episodes.


When you have made a selection, the download starts::

    Ready to download 1 programs, with total duration 0:11:02
    Downloading:  26%|███████▊                      | 173/662 [00:10<00:11, 43.9s/s]

The progress bar shows the number of seconds of video to be downloaded,
in this case 0:11:02 = 11*60 + 2 = 662 seconds. The next two times are
the estimated remaining and total download time. The last number shows how
many seconds of video are downloaded per second. So in this snapshot, the
video was downloaded at 44x the playback speed.

If you have already downloaded some of the episodes, those will be
automatically skipped (not overwritten).


Downloading without interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to download all available episodes with no questions asked, use
the ``--all`` option on the command line.
Or if you want to download only the latest episode, use
the ``--last`` option on the command line.
If you use any of these options, you will not be asked for what program
to download. This allows for running ``nrkdownload`` as a scheduled job,
e.g. via cron.



Downloading seasons
-------------------

If you are only interested in a specific season of a series, click around on
the webpages until you are only looking at that season. As an example, if you
wanted to download the third season of SKAM, you would use an URL like
https://tv.nrk.no/serie/skam/sesong/3


Downloading programs
--------------------

For downloading a specific program that is not part of a series, the URL
could look like e.g. https://tv.nrk.no/program/KOID28004110/pushwagner


Downloading podcasts
--------------------

Similarly to TV-series and episodes, you can specify the URL for the
whole podcast series or for a specific episode. An example for a whole
podcast series would be https://radio.nrk.no/podkast/sjakksnakk/ whereas
https://radio.nrk.no/podkast/sjakksnakk/nrkno-poddkast-26616-142542-23102018091100
refers to a specific episode::

    $ nrkdownload https://radio.nrk.no/podkast/sjakksnakk/

    Matching programs
     0: Sjakksnakk - Episode 1 - #1 Magnus Carlsen frykter å tape (2018-10-23)
     1: Sjakksnakk - Episode 2 - #2 Simen Agdestein om ensomheten på toppen...
     2: Sjakksnakk - Episode 3 - #3 Jon Ludvig Hammer om livet i Carlsens s...
     3: Sjakksnakk - Episode 4 - #4 Ellen Carlsen og Heidi Røneid frykter a...
     4: Sjakksnakk - Episode 5 - #5 Hans Olav Lahlum mener Carlsen søker sj...
     5: Sjakksnakk - Episode 6 - #6 Torstein Bae og Atle Grønn tror VM blir...

    Enter a number or Python-style interval (e.g. 8 or -2: or : ). (q to quit): :
    Podcast 1 of 6: 91.2Mb [00:00, 175Mb/s]
    Podcast 2 of 6: 60.9Mb [00:00, 181Mb/s]
    Podcast 3 of 6: 58.8Mb [00:00, 181Mb/s]
    Podcast 4 of 6: 74.6Mb [00:00, 177Mb/s]
    Podcast 5 of 6: 67.4Mb [00:00, 170Mb/s]
    Podcast 6 of 6: 83.5Mb [00:00, 133Mb/s]

