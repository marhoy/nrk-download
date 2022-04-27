Installing nrkdownload
======================


Installing or upgrading to the latest release of nrkdownload
------------------------------------------------------------

The package is avaible via `PyPI <https://pypi.org/project/nrkdownload/>`_. The
recommended way to install ``nrkdownload`` is by using `pipx
<https://pypa.github.io/pipx/installation/>`_. ``pipx`` is a tool that installs and runs
Python applications in isolated environments. If you haven't already done so, start by
installing pipx, and then install, upgrade or uninstall ``nrkdownload`` like this::
    
    $ pipx install nrkdownload
    $ pipx upgrade nrkdownload
    $ pipx uninstall nrkdownload

Note that in order to download video and subtitles, an installation of ``ffmpeg`` is
needed. See :doc:`/30_installing_ffmpeg`.
