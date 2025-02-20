Installing nrkdownload
======================


Installing or upgrading to the latest release of nrkdownload
------------------------------------------------------------

The nrkdownload package is avaible via `PyPI <https://pypi.org/project/nrkdownload/>`_.

To install ``nrkdownload`` as a CLI tool in your environment, you can use e.g. `pipx
<https://pipx.pypa.io/stable/installation/>`_ or `uv
<https://docs.astral.sh/uv/getting-started/installation/>`_.  Both ``pipx`` and ``uv``
have the ability to install and runs Python applications in isolated environments.


With ``pipx``, you would do::
    
    $ pipx install nrkdownload
    $ pipx upgrade nrkdownload
    $ pipx uninstall nrkdownload


With ``uv``, you would do::

    $ uv tool install nrkdownload
    $ uv tool upgrade nrkdownload
    $ uv tool uninstall nrkdownload


Note that in order to download video and subtitles, an installation of ``ffmpeg`` is
also needed. See :doc:`/30_installing_ffmpeg`.
