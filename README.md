# nrkdownload

!["Build status"](https://img.shields.io/github/actions/workflow/status/marhoy/nrk-download/main.yml)
[![codecov](https://codecov.io/gh/marhoy/nrk-download/branch/main/graph/badge.svg?token=84LOP32NP6)](https://codecov.io/gh/marhoy/nrk-download)
!["Latest version"](https://img.shields.io/pypi/v/nrkdownload)
!["Supported Python versions"](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fmarhoy%2Fnrk-download%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

This is a commandline tool to download programs and series from NRK (Norwegian public
broadcaster). It supports both TV, Radio and Podcast content. The tool is written in
Python, and is compatible with Python 3.10 or newer. It has been tested under Linux, Mac
OS X and Windows.

# Documentation

The documentation for nrkdownload is availabe here: https://nrkdownload.readthedocs.io

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
- Merge the PR to the `main` branch
- Create a new tag nameed `vX.Y.Z` where `X.Y.Z` is the new version number
- The new version of the package will be published to PyPi automatically
- Optionally create a new release on GitHub, based on the new tag
