# nrkdownload

!["Latest version"](https://img.shields.io/github/v/release/marhoy/nrk-download?include_prereleases)

!["Supported Python versions"](https://img.shields.io/pypi/pyversions/nrkdownload)

This is a commandline tool to download programs and series from NRK (Norwegian public
broadcaster). It supports both TV, Radio and Podcast content. The tool is written in
Python, and is compatible with Python 3.7 or newer. It has been tested under Linux, Mac
OS X and Windows.

# Documentation

The documentation for nrkdownload is availabe here: https://nrkdownload.readthedocs.org

# Setting up a development environment

Install [poetry](https://python-poetry.org/), and a recent Python version (>=3.7). If
you want to run tests with multiple Python versions, install
[pyenv](https://github.com/pyenv/pyenv). Set up the development environment:

```bash
poetry install
```

# Making a new release

- Make sure all tests are ok by running `tox`
- Make a pull requst on GitHub
- Use the "new release" functionallity of GitHub. Make a new tag.
- Update `pyproject.toml` and `__init__.py` to match the new version number.
- `poetry build`
- `poetry publish`
