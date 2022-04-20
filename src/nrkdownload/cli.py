import sys
from pathlib import Path
from typing import List, Optional

import typer
from halo import Halo
from loguru import logger

from nrkdownload.nrk_tv import NotPlayableError, TVProgram, TVSeries, TVSeriesType


def set_loglevel(verbosity: int):
    levels = {0: "WARNING", 1: "SUCCESS", 2: "INFO", 3: "DEBUG", 4: "TRACE"}
    log_level = levels[verbosity]
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.success(f"Setting loglevel to {log_level}")


def series(
    series_id: str, download_dir: Path, only_seasons: Optional[List[str]] = None
):
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
        if (only_seasons is not None) and (info.season_id not in only_seasons):
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


def program(program_id: str, download_dir: Path):
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


def main(
    urls: List[str] = typer.Argument(
        ..., help="One or more valid URLs from https://tv.nrk.no/"
    ),
    download_dir: Path = typer.Option(
        Path.home() / "Downloads" / "nrkdownload",
        "--download-dir",
        "-d",
        help="Download directory",
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
):
    typer.echo(f"Downloading to {download_dir}:")
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

        series(url, download_dir)
        # program(url, download_dir)


def entrypoint():
    typer.run(main)


if __name__ == "__main__":
    entrypoint()
