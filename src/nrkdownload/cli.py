import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import pkg_resources
import typer
from halo import Halo
from loguru import logger

from nrkdownload.nrk_tv import NotPlayableError, TVProgram, TVSeries, TVSeriesType

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
        raise typer.Exit()


def download_series(
    series_id: str, download_dir: Path, only_season_id: Optional[str] = None
) -> None:
    """_summary_

    Args:
        series_id (_type_): _description_
        download_dir (_type_): _description_
        only_seasons (_type_, optional): _description_. Defaults to None.
    """
    series = TVSeries.from_series_id(series_id)
    typer.echo(f"Downloading {series.title}")
    series.download_images(download_dir)
    for info in series.season_info:
        if (only_season_id is not None) and (info.season_id != only_season_id):
            continue
        season = series.get_season(info.season_id)
        typer.echo(f"Downloading {season.title}")
        season.download_images(download_dir / series.dirname)
        directory = download_dir / series.dirname / season.dirname
        with typer.progressbar(season.episodes) as episodes:
            for episode_number, program_id in enumerate(episodes, start=1):
                try:
                    program = TVProgram.from_program_id(program_id)
                except NotPlayableError as e:
                    typer.echo(f"Skipping: {e}")
                    continue
                if series.type == TVSeriesType.sequential:
                    sequence_string = f"s{season.season_id:>02s}e{episode_number:>02d}"
                else:
                    sequence_string = season.season_id
                program.download_as_episode(series.title, sequence_string, directory)
                # typer.echo(f"Downloading episode {program.title}")


def download_program(program_id: str, download_dir: Path) -> None:
    """_summary_

    Args:
        program_id (_type_): _description_
        download_dir (_type_): _description_
    """
    try:
        program = TVProgram.from_program_id(program_id)
    except NotPlayableError as e:
        typer.echo(f"Skipping: {e}")
        return
    with Halo(text=f"{program.title}", spinner="dots") as spinner:
        program.download_as_program(download_dir / program.title)
        spinner.succeed()


def get_default_dowload_dir() -> Path:
    dir = os.environ.get("NRKDOWNLOAD_DIR") or Path.home() / "Downloads" / "nrkdownload"
    return Path(dir)


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
    ),
) -> None:
    for url in urls:
        # Example program URL:
        # https://tv.nrk.no/program/KOID75000320
        #
        # Example "sequential" series URL:
        # https://tv.nrk.no/serie/kongen-av-gulset
        # https://tv.nrk.no/serie/kongen-av-gulset/sesong/1
        # https://tv.nrk.no/serie/kongen-av-gulset/sesong/1/episode/3/avspiller
        #
        # Example "standard" series URL:
        # https://tv.nrk.no/serie/klassequizen
        # https://tv.nrk.no/serie/klassequizen/2021
        # https://tv.nrk.no/serie/klassequizen/2021/DSRR21000521/avspiller
        #
        # Example "news" series URL:
        # https://tv.nrk.no/serie/dagsrevyen-21
        # https://tv.nrk.no/serie/dagsrevyen-21/202203
        # https://tv.nrk.no/serie/dagsrevyen-21/202203/NNFA21030122/avspiller

        if match := re.match(
            r"https://tv.nrk.no/serie/([\w-]+)(?:/sesong/(\w+)|/(\w+)|)", url
        ):
            series_id = match.group(1)
            only_season_id = match.group(2) or match.group(3)
            download_series(series_id, download_dir, only_season_id)

        elif match := re.match(r"https://tv.nrk.no/program/(\w+)", url):
            program_id = match.group(1)
            download_program(program_id, download_dir)
        else:
            typer.echo("Not able to parse URL")
            typer.Exit(1)
