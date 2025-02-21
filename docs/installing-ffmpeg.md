# Installing FFmpeg

The videos and subtitles are downloaded using
[FFmpeg](https://www.ffmpeg.org/download.html). It is available for all major operating
systems. You need to install ffmpeg and make it available in your `$PATH` before you can
use `nrkdownload`.

## For Windows

Should be rather straight forward. Download the latest static build and
run the installer.

## For Linux

Depending on your Linux-distribution, you might have to add a
package-repository in order to install ffmpeg. If you get stuck, try too
Google installing ffmpeg for YOUR_LINUX_DISTRO.

## For macOS

The easiest way to install and update ffmpeg is maybe via [Homebrew](https://brew.sh/).
After installing Homebrew itself, you can just say:

```{ .shell }
brew install ffmpeg
```
