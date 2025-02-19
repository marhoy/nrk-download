# nrkdownload

!["Latest version"](https://img.shields.io/github/v/release/marhoy/nrk-download?include_prereleases)

!["Supported Python versions"](https://img.shields.io/pypi/pyversions/nrkdownload)

This is a commandline tool to download programs and series from NRK (Norwegian public
broadcaster). It supports both TV, Radio and Podcast content. The tool is written in
Python, and is compatible with Python 3.8 or newer. It has been tested under Linux, Mac
OS X and Windows.

# Documentation

The documentation for nrkdownload is availabe here: https://nrkdownload.readthedocs.org

# Setting up a development environment

Install [uv](https://docs.astral.sh/uv/). To set up the development environment:

```bash
uv sync --group docs
pre-commit install
```

# Making a new release

- Make sure all tests are ok by running `nox`
- Make sure all pre-commit hooks are ok by running `pre-commit run --all-files`
- Make a pull requst on GitHub
- Merge the PR to master.
- Use the "new release" functionallity of GitHub. Make a new tag.
- The release will be published to PyPi automatically.
