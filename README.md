# nrkdownload
![Supports python 2.7, 3.3, 3.4, 3.5, 3.6, 3.7](https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5%2C%203.6%2C%203.7-brightgreen.svg "Supported Python versions")

This is a commandline tool to download programs and series from NRK (Norwegian public broadcaster). It supports both TV, Radio and Podcast content. The tool is written in Python, and is compatible with Python 2.7 and 3.x. It has been tested under Linux, Mac OS X and Windows.

# Documentation
The documentation for nrkdownload is availabe here:
https://nrkdownload.readthedocs.org

# Making a new release
- Make sure all tests are ok: `tox`
- Push changes to GitHub
- Use the "new release" functionallity of GitHub. Make a new tag.
- `python setup.py sdist bdist_wheel`
- `twine upload dist/*`
