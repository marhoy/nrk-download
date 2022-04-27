Usage
==================

Start by browsing https://tv.nrk.no until you find what you want. Copy the URLs and give
it as an argument for this tool. You can list several URLs on the command line
(separated by space). Content that are already downloaded will be skipped.


Options
-------

  Usage: nrkdownload [OPTIONS] URLS...

  Arguments:
    URLS...  One or more valid URLs from https://tv.nrk.no/  [required]

  Options:
    -d, --download-dir PATH  Download directory. Can also be specified by
                            setting the environment variable NRKDOWNLOAD_DIR
                            [default: /Users/marhoy/Downloads/nrkdownload]
    --version                Print version string
    -v                       Increase logger verbosity. Can be repeated up to
                            four times.  [default: 0; x<=4]
    --help                   Show this message and exit.


The files are by default downloaded to ~/Downloads/nrkdownload. This can be changed by
using the option -d as described above, or you can define the environment variable
NRKDOWNLOAD_DIR


URL Parsing and actions
-----------------------

If the URL points to the top-level of a series, all episodes in all seasons will be
downloaded. If the URL points to a specific season, only the episodes within that season
will be downloaded.
