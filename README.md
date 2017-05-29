# nrkdownload
![Supports python 2.7, 3.3, 3.4, 3.5, 3.6](https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5%2C%203.6-brightgreen.svg "Supported Python versions")

This is yet another commandline tool to download programs and series from NRK (Norwegian public broadcaster). It is inspired by the already existing tools that you can find on GitHub. The reason I decided to make yet another tool, was that I found the source code of some of the other tools to be difficult to read and understand, and thus difficult to contribute to.

The tool is written in Python, and is compatible with Python 2.7 and 3.x. It has been tested under both Linux, MacOS and Windows.

## What does this tool add?
When you download a program with this tool, it doesn't just download that file. If the program is part of a series, directories for that series and season is created. And the file is automatically named according to its episode and season number. Subtitles and additional images are also automatically downloaded. The subtitles are automatically embedded in the .m4v-file, so you could decide to delete the .srt-file. (I have found that in some tools (like VLC), the support for included subtitles is not perfect. That's why the separate .srt-file is also there.)

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

# Usage
There are two ways do download things:
1. You can interactively search for content. You have to specify whether you are searching for a particular program, or if you are searching for a series. You will go through a selection process in order to identify what is to be downloaded.
1. You can specify an URL that identifies the content that you want to dowload. The URL is typically copied from https://tv.nrk.no/. In this case, the download starts with no questions asked.
```
$ nrkdownload -h
usage: nrkdownload [-h] [--version] [-d DIRECTORY]
                   (-p PROGRAM | -s SERIES | -u URL)

Download series or programs from NRK, complete with images and subtitles.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d DIRECTORY          The directory where the downloaded files will be
                        placed
  -p PROGRAM, --program PROGRAM
                        Search for a program that matches the string PROGRAM.
                        Interactive download.
  -s SERIES, --series SERIES
                        Search for a series that matches the string SERIES.
                        Interactive download
  -u URL, --url URL     Download whatever is specified by URLs, no questions
                        asked. URLs can be copied from https://tv.nrk.no/

The files are by default downloaded to ~/Downloads/nrkdownload. This can be
changed by using the option -d as described above, or you can define the
environment variable NRKDOWNLOAD_DIR
```

## Searching for a series
Let's say you are interested in downloading all the available episodes about the rescue boat "Elias". You would then use the flag `-s` to specify that you are searching for a series with the name Elias. If there is more than one matching series, you will be asked to specify which one of them you want. You respond to this by typing an integer and pressing Enter. If there is only one matching series, it skips directly to the next step:

Then, all of the registered episodes will be listed (due to copyright-issues, some of them might not be available for download). You then will be asked to specify what episodes you want to download. You respond to this by typing an integer or a range. The range can be specified in different ways:
- `5-10` or `5:10`, means all episodes from 5 to 10, including both 5 and 10.
- `-10` or `:10`, means all episodes from the start (0) to 10, including both 0 and 10.
- `10-` or `10:`, means all episodes from 10 to the last, including both 10 and the last.
- `-` or `:`, means all available episodes.

So the above would typically look like this in your terminal:
```
$ nrkdownload -s elias

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

Enter a number or interval (e.g. 8 or 5-10). (q to quit): -10
Getting program details for your selection of 11 programs...
Ready to download 11 programs, with total duration 2:01:02
Downloading:  35%|█████████                 | 2.52K/7.26K [01:25<02:22, 33.1s/s]
```
The progress bar shows the number of seconds of video to be downloaded, in this case 2:01:02 = 2*3600 + 62 = 7262 seconds. The next two times are the estimated remaining and total download time. The last number shows how many seconds of video are downloaded per second. So in this snapshot, the video was downloaded at 33x the playback speed. 

If you have already downloaded some of the episodes, those will be automatically skipped (not overwritten).

## Searching for a program
If you were interested in programs where the name "Elias" was mentioned (as opposed to the series "Elias", as described above), you would specify that by using the flag `-p`. The results from the search will be programs, so all you have to do is to specify the program(s) you want by using the range syntax described above.

Note that if your search string consists of more than one word, you must surround it with single or double quotes.

In your terminal, that would look like this:
```
$ nrkdownload -p "redningsskøyta elias"

Matching programs
 0: Gratulerer med dagen! (2011): Gratulerer med dagen! 17.05.2011 - 17.05.2011 - S34E01
 1: Dagsrevyen (Januar 2013): Dagsrevyen 10.01.2013 - 10.01.2013 - S36E10
⋮
 6: Supernytt (2015): Supernytt 06.05.2015 - 06.05.2015 - S06E80
 7: Barne-tv - hele sendinger (2017): Barne-tv - 12.01.2017 - S02E12

Enter a number or interval (e.g. 8 or 5-10). (q to quit): 
```

## Download target specified by URL
If you know exactly what you want to download, there is no need to go through the interactive search described above. Instead, you can just specify the download target directly with an URL. You will typically find these URLs by browsing https://tv.nrk.no. Examples of such URLs could be:
* https://tv.nrk.no/serie/skam: This will download ALL the episodes of ALL the seasons of this series.
* https://tv.nrk.no/serie/skam/MYNT15000117/sesong-4/episode-1 (or just https://tv.nrk.no/serie/skam/MYNT15000117): This will dowload the specified episode of that series.
* https://tv.nrk.no/program/KMTE50001515/svartedauden (or just https://tv.nrk.no/program/KMTE50001515): This will download the specified program.

The download is not interactive when you specify an URL, which means you can automatically download content from scripts or cron-jobs. Files that are already downloaded will be skipped.

TODO: Support will be added for specifying several URLs at the same time, either from stdin or from file.

## Configurable download directory
If you don't specify anything, the files and directories will be created inside `~/Downloads/nrkdownload`, where `~` means your home directory. If you want the downloads somewhere else (e.g. directly to your NAS), there are two ways to specify a different download directory:
- Define an environment variable named `NRKDOWNLOAD_DIR`
- Specify the download directory on the command line with the option `-d download_dir`

If you do both at the same time, the option from the command line will take precedence.

If you don't know how to define an environment variable under your operating system, try to Google `create environment variable` and the name of you operating system. (Under Linux and MacOS, you would want to edit your `~/.bash_profile`)

# Installing
The nrkdownload package and its requirements can be installed in several ways, depending on whether you want to just use it or whether you want to change the code. And since it is compatible with both Python 2 and 3, you can decide under what version of Python you want to run it.

## All operating systems
In general, you should try to avoid installing python packages as root (Administrator), and keep your global Python-installation clean (and under control of you OS package manager (like rpm or deb)). This can be achieved in several ways:

1. Install Python packages under your own home-directory by passing the `--user` option to the `pip` installer.
2. Install your own user-specific Python distribution, where you can later install packages. [Anaconda](https://www.continuum.io/downloads) is a good choice. It also has good support for environments (see next).
3. Create a virtual environment using [standard Python](https://docs.python.org/3/tutorial/venv.html) or [conda](https://conda.io/docs/using/envs.html) (used by Anaconda) and install packages in there.


## Special considerations for MacOS (OS X)
MacOS comes by default with an installation of Python 2.7. You can decide to go with this (i.e. not installing Anaconda as mentioned above). In order to install packages you need the package installer `pip`, and under MacOS `pip` is not installed by default. You can install it by typing `sudo easy_install pip`. In order to utilize the `--user` scheme described above, you must also add `~/Library/Python/2.7/bin` to your $PATH (edit your `~/.bash_profile`). This enables installed Python scripts (like nrkdownload) to be available in the Terminal.

Also, if you get an `UnicodeEncodeError`, add the following line to your  `~/.bash_profile`:
`export LC_CTYPE=en_US.UTF-8`

## Special considerations for Linux
Your system might have both Python 2 and 3 installed as a part of the Linux-distribution. If Python 2 is the default, `pip` will be pointing to the Python 2 installation, whereas `pip3` will point to the Python 3 installation. If that is the case for you, and you explicitly want to run nrkdownload under Python 3, you must replace `pip` with `pip3` in the examples below.

## Special considerations for Windows
Windows does not come with an installation of Python. You can choose to install version 2.7.x or the latest 3.x from [python.org](https://www.python.org/). If you want to learn and develop Python I would suggest [Anaconda](https://www.continuum.io/downloads), which installs in your home-directory and comes with a nice selection of packages.

## Installing the latest release of nrkdownload
In the following examples, packages are installed with the [user scheme](https://pip.pypa.io/en/stable/user_guide/#user-installs) described in example 1 above.
```
$ pip install --user nrkdownload
```
If you at some point want to upgrade to a newer version, just add a `-U` (for Upgrade):
```
$ pip install -U --user nrkdownload
```

## Installing the latest revision directly from GitHub:
```
$ pip install --user git+https://github.com/marhoy/nrk-download.git#egg=nrkdownload
```
If you at some point want to upgrade to a newer version, use `-U` as described above.

## Installing in development mode:
If you want to change (and possibly contribute to) the code, first clone the repository. This will create a directory containing a local copy of the GitHub-repository. Then install in develop mode from this directory:
```
$ git clone https://github.com/marhoy/nrk-download.git
$ pip install --user -e nrk-download
```
You will then be able to use the tool as usual, but the installation will be a pointer to your local repository. Whatever changes you make in your local repository will have immediate effect on the "installation".

# Uninstalling nrkdownload
To unistall nrkdownload, just type:
```
$ pip uninstall nrkdownload
```
NOTE: This will not uninstall the required packages that might have been installed together with nrkdownload. Type `pip list --user` to list all user-installed packages, and uninstall them if you know that you don't need them anymore.

# FFmpeg
The videos and subtitles are downloaded using [FFmpeg](https://ffmpeg.org/). It is available for all major operating systems. You need to install ffmpeg and make it available in your $PATH before you can use nrkdownload.

## For Linux
Depending on your Linux-distribution, you might have to add a package-repository in order to install ffmpeg. If you get stuck, try too Google `installing ffmpeg for YOUR_LINUX_DISTRO`.

## For MacOS
Download the static build of the latest release (currently 3.2.2). Open the .dmg-file and copy the binary file `ffmpeg` to e.g. a directory `bin` inside your home directory. Then, add ~/bin to your PATH.


## More metadata?
The m4v-format has support for builtin metadata. We could add some information there. Also: Both series and programs/episodes have a description at tv.nrk.no. It could possibly be interesting to save these descriptions to a text file.
