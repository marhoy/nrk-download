Examples
========

Dowloading series
-----------------

Let's say you are interested in downloading all the available episodes about
the rescue boat "Elias". You would then search for "Elias" on https://tv.nrk.no
and end up at a page with the URL https://tv.nrk.no/serie/elias. This is the
URL you want to give as argument to ``nrkdownload``.

Then, all of the registered episodes will be listed, numbered from 0.
Due to copyright-issues, some of the episodes might not be available for
download. You then will be asked to specify what episodes you want to
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


If you want to download all available episodes with no questions asked, use
the ``--all`` option. Or if you want to download only the latest episode, use
the ``--last`` option. Using these two options allows you to run the download
without interaction, suitable for a e.g. a scheduled cronjob.



Downloading seasons
-------------------

If you are only interested in a specific season if a series, click around on
the webpages until you are only looking at that season. As an example, if you
wanted to download the third season of SKAM, you would use an URL like
https://tv.nrk.no/serie/skam/sesong/3


Downloading programs
--------------------

For downloading a specific program that is not part of a series, the URL
could look like e.g. https://tv.nrk.no/program/KOID28004110/pushwagner


Downloading podcasts
--------------------
