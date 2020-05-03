# nrkdownload
![Supports python 2.7, 3.6, 3.7, 3.8](https://img.shields.io/badge/python-2.7%2C%203.6%2C%203.7%2C%203.8-brightgreen.svg "Supported Python versions")

This is a commandline tool to download programs and series from NRK (Norwegian public broadcaster). It supports both TV, Radio and Podcast content. The tool is written in Python, and is compatible with Python 2.7 and 3.x. It has been tested under Linux, Mac OS X and Windows.

# Documentation
The documentation for nrkdownload is availabe here:
https://nrkdownload.readthedocs.org

# Setting up a development environment
Install [poetry](https://python-poetry.org/), and a recent Python version (>=3.6).
If you want to run tests with multiple Python versions, install [pyenv](https://github.com/pyenv/pyenv).
Set up the development environment:
```bash
poetry install
```


# Making a new release
- Make sure all tests are ok by running `tox`
- Make a pull requst on GitHub
- Use the "new release" functionallity of GitHub. Make a new tag.
- Update `pyproject.toml` to match the new version number.
- `poetry build`
- `poetry publish`
