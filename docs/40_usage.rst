Usage
==================

Before NRK restricted the API, it was possible to search for content. With
the current restrictions, you will need to specify an URL for the content you
want to download: Start by browsing https://tv.nrk.no (possibly
https://tv.nrksuper.no/) or https://radio.nrk.no
until you find what you want. Copy the URLs and give it as arguments for this
tool. You can list several URLs on the command line (separated by space),
or line by line in a file. Content that are already downloaded will be skipped.


Options
-------

usage: nrkdownload [-h] [--version] [-d DIRECTORY] [-v] [-c] [-a | -l]
                   [-f FILE]
                   [URL [URL ...]]

Download series or programs from NRK, complete with images and subtitles.

positional arguments:
  URL                   Specify download source(s). Browse https://tv.nrk.no/
                        or https://radio.nrk.no/ and copy the URL. The URL can
                        point to a whole series, or just one episode.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d DIRECTORY          The directory where the downloaded files will be
                        placed
  -v, --verbose         Increase verbosity. Can be repeated up to two times.
  -c, --cache           Enable persistent caching of the API requests.
  -a, --all             If URL matches several episodes: Download all episodes
                        without asking.
  -l, --last            If URL matches several episodes: Download the latest
                        without asking.
  -f FILE, --file FILE  Specify a file containing URLs, one URL per line.
                        Specifying urls from a file will automatically enable
                        --all and download all episodes from series.

The files are by default downloaded to ~/Downloads/nrkdownload. This can be
changed by using the option -d as described above, or you can define the
environment variable NRKDOWNLOAD_DIR



Configurable download directory
-------------------------------

If you don't specify anything, the files and directories will be created
inside ``~/Downloads/nrkdownload``, where ``~`` means your home directory.
If you want the downloads somewhere else, there are two ways to specify a
different download directory:

* Define an environment variable named ``NRKDOWNLOAD_DIR``
* Specify the download directory on the command line with the option
  ``-d download_dir``

If you do both at the same time, the option from the command line will take
precedence.

If you don't know how to define an environment variable under your operating system, try to Google create environment variable and the name of you operating system. (Under Linux and macOS, you would want to edit your ~/.bash_profile)

