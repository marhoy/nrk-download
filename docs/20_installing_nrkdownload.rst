Installing nrkdownload
======================


Installing or upgrading to the latest release of nrkdownload
------------------------------------------------------------

To install or upgrade to the latest release from
`PyPI <https://pypi.org/project/nrkdownload/>`_ , use the following
command::

    $ pip install -U --user nrkdownload

For considerations on Python 2 vs. 3 and the ``--user`` option,
see the section on :ref:`considerations` below.


Installing in development mode:
-------------------------------

If you want to change (and possibly contribute to) the code, first
clone the GitHub repository. This will create a directory containing a local
copy. Then install in develop mode from this directory::

    $ git clone https://github.com/marhoy/nrk-download.git
    $ pip install --user -e nrk-download

You will then be able to use the tool as usual, but the installation
will be a pointer to your local repository. Whatever changes you make
in your local repository will have immediate effect on the "installation".

You are welcome to help developing ``nrkdownload``, please see the section
on :ref:`contributing`.


Uninstalling nrkdownload
------------------------

To uninstall nrkdownload, just type::

    $ pip uninstall nrkdownload

NOTE: This will not uninstall the required packages that might have
been installed together with nrkdownload. Type ``pip list --user`` to
list all user-installed packages, and uninstall them if you know that
you don't need them anymore.


.. _considerations:

OS considerations
-----------------

This tool is compatible with both Python 2 and 3. But unless you have
other reasons to use Python 2, the latest Python 3.x is recommended.

If your system-wide Python installation is under control of a package
manager like rpm or deb, you should avoid pip-installing python
packages as root. This can be solved in several ways:

#. Install Python packages under your own home-directory by passing the
   ``--user`` option to the pip installer.
#. Install your own user-specific Python distribution, where you can
   later install packages. Anaconda (or Miniconda) is a good choice.
   It also has good support for environment (see next).
#. Create a virtual environment using standard Python or conda
   (used by Anaconda/Miniconda) and install packages in that environment.



Special considerations for MacOS (OS X)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MacOS comes by default with an installation of Python 2.7. You can decide
to go with this (i.e. not installing Anaconda as mentioned above).
In order to install packages you need the package installer pip, and
under macOS pip is not installed by default. You can install it by
typing ``sudo easy_install pip``.
In order to utilize the ``--user`` scheme described above, you must
also add ``~/Library/Python/2.7/bin`` to your
``$PATH`` (edit your ``~/.bash_profile``).
This enables installed Python scripts (like nrkdownload) to be
available in the Terminal.

Also, if you get an ``UnicodeEncodeError``, add the following line
to your  ``~/.bash_profile``:
``export LC_CTYPE=en_US.UTF-8``



Special considerations for Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Your system might have both Python 2 and 3 installed as a part of
the Linux-distribution. If Python 2 is the default, ``pip`` will be
pointing to the Python 2 installation, whereas ``pip3`` will point
to the Python 3 installation. If that is the case for you, and you
explicitly want to run nrkdownload under Python 3, you must
replace ``pip`` with ``pip3`` in the examples above.



Special considerations for Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows does not come with an installation of Python.
You can choose to install version 2.7.x or the latest 3.x from
python.org. If you want to learn and develop Python I would suggest
Anaconda, which installs in your home-directory and comes with
a nice selection of packages.

