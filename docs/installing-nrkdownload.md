# Installing or upgrading nrkdownload

The `nrkdownload` package is avaible for installation from
[PyPI](https://pypi.org/project/nrkdownload/).

To install `nrkdownload` as a CLI tool in your environment, you can use e.g.
[pipx](https://pipx.pypa.io/stable/installation/) or
[uv](https://docs.astral.sh/uv/getting-started/installation/). Both `pipx` and `uv` have
the ability to install and run Python applications in isolated environments.

With `pipx`, you would do::

```{ .shell .copy }
pipx install nrkdownload
pipx upgrade nrkdownload
# pipx uninstall nrkdownload
```

With `uv`, you would do::

```{ .shell .copy }
uv tool install nrkdownload
uv tool upgrade nrkdownload
# uv tool uninstall nrkdownload
```

Note that in order to download video and subtitles, an installation of `ffmpeg` is also
needed. See [Installing FFmpeg](installing-ffmpeg.md).
