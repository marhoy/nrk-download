import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import pkg_resources
import typer
from loguru import logger

from nrkdownload.download import (
    download_program,
    download_series,
    get_default_dowload_dir,
)

app = typer.Typer(add_completion=False)


def set_loglevel(verbosity: int) -> None:
    levels = {0: "WARNING", 1: "SUCCESS", 2: "INFO", 3: "DEBUG", 4: "TRACE"}
    log_level = levels[verbosity]
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.success(f"Setting loglevel to {log_level}")


def version_callback(value: bool) -> None:
    if value:
        version = pkg_resources.require("nrkdownload")[0].version
        typer.echo(f"nrkdownload version: {version}")
        raise typer.Exit(code=0)


def match_program_url(url: str) -> Optional[str]:
    if match := re.match(r"https://tv.nrk.no/program/(\w+)", url):
        return match.group(1)
    return None


def match_series_url(url: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    if match := re.match(
        r"https://tv.nrk.no/serie/([\w-]+)(?:/sesong/(\w+)|/(\w+)|)(?:/episode/(\w+)|/(\w+)|)",  # noqa: E501
        url,
    ):
        series_id = match.group(1)
        season_id = match.group(2) or match.group(3)
        episode_id = match.group(4) or match.group(5)
        return series_id, season_id, episode_id
    return None


@app.command()
def main(
    urls: List[str] = typer.Argument(
        ..., help="One or more valid URLs from https://tv.nrk.no/"
    ),
    download_dir: Path = typer.Option(
        get_default_dowload_dir(),
        "--download-dir",
        "-d",
        help=(
            "Download directory. Can also be specified by setting the environment "
            "variable NRKDOWNLOAD_DIR"
        ),
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Print version string",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: int = typer.Option(
        0,
        "-v",
        count=True,
        callback=set_loglevel,
        help="Increase logger verbosity. Can be repeated up to four times.",
        max=4,
        clamp=True,
        is_eager=True,
    ),
) -> None:
    for url in urls:
        if program_id := match_program_url(url):
            download_program(download_dir, program_id)
        elif match := match_series_url(url):
            series_id, season_id, episode_id = match
            download_series(download_dir, series_id, season_id, episode_id)
        else:
            typer.echo("Not able to parse URL")
            raise typer.Exit(code=1)
