"""CLI for nrkdownload."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Annotated

import typer
from ffmpeg import FFmpeg
from loguru import logger

from nrkdownload import __version__
from nrkdownload.download import (
    download_program,
    download_series,
)

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "nrkdownload"

app = typer.Typer(add_completion=False)


def set_loglevel(verbosity: int) -> None:
    """Set loguru loglevel."""
    log_levels = {
        0: "WARNING",
        1: "SUCCESS",
        2: "INFO",
        3: "DEBUG",
        4: "TRACE",
    }
    logger.remove()
    logger.add(sys.stderr, level=log_levels[verbosity])
    logger.success(f"Setting loglevel to {log_levels[verbosity]}")


def version_callback(value: bool) -> None:
    """Print version info."""
    if value:
        typer.echo(f"nrkdownload version: {__version__}")
        raise typer.Exit()


def match_program_url(url: str) -> str | None:
    """Figure out if the URL is a program URL."""
    if match := re.match(r"https://tv.nrk.no/program/(\w+)", url):
        return match.group(1)
    return None


def match_series_url(url: str) -> tuple[str, str | None, str | None] | None:
    """Figure out if the URL is a series URL."""
    if match := re.match(
        r"https://tv.nrk.no/serie/([\w-]+)(?:/sesong/(\w+)|/(\w+)|)(?:/episode/(\w+)|/(\w+)|)",
        url,
    ):
        series_id = match.group(1)
        season_id = match.group(2) or match.group(3)
        episode_id = match.group(4) or match.group(5)
        return series_id, season_id, episode_id
    return None


@app.command()
def main(
    urls: Annotated[
        list[str],
        typer.Argument(..., help="One or more valid URLs from https://tv.nrk.no/"),
    ],
    download_dir: Annotated[
        Path,
        typer.Option(
            "-d",
            "--download-dir",
            file_okay=False,
            dir_okay=True,
            envvar="NRKDOWNLOAD_DIR",
            help=(
                "Download directory. Can also be specified by setting the environment "
                "variable NRKDOWNLOAD_DIR."
            ),
        ),
    ] = DEFAULT_DOWNLOAD_DIR,
    with_extras: Annotated[
        bool,
        typer.Option(
            "--with-extras/--without-extras",
            help="Download extra material for series.",
        ),
    ] = False,
    _version: Annotated[
        bool | None,
        typer.Option(
            "-V",
            "--version",
            help="Print version string",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    _verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            callback=set_loglevel,
            help="Increase logger verbosity. Can be repeated up to four times.",
            show_default=False,
            count=True,
            max=4,
            clamp=True,
        ),
    ] = 0,
) -> None:
    """Download content from https://tv.nrk.no/."""
    try:
        ffmpeg_version = FFmpeg().option("version").execute().decode("utf-8")
        logger.info(f"FFmpeg version: {ffmpeg_version.splitlines()[:2]}")
    except FileNotFoundError:
        typer.echo(
            "\nFFmpeg not found, must be installed to use this package.\n"
            "See documentation: https://nrkdownload.readthedocs.io/"
        )
        raise typer.Exit(1) from None

    for url in urls:
        if program_id := match_program_url(url):
            download_program(download_dir, program_id)
        elif match := match_series_url(url):
            series_id, season_id, episode_id = match
            download_series(download_dir, series_id, with_extras, season_id, episode_id)
        else:
            typer.echo("Not able to parse URL")
            raise typer.Exit(code=1)
