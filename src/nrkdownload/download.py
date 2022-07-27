import os
from pathlib import Path
from typing import Optional

import typer
from halo import Halo
from loguru import logger

from nrkdownload.nrk_tv import (
    NotPlayableError,
    TVProgram,
    TVSeries,
    TVSeriesType,
    valid_filename,
)


def get_default_dowload_dir() -> Path:
    dir = os.environ.get("NRKDOWNLOAD_DIR") or Path.home() / "Downloads" / "nrkdownload"
    return Path(dir)


def download_series(
    download_dir: Path,
    series_id: str,
    only_season_id: Optional[str] = None,
    only_episode_id: Optional[str] = None,
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
            logger.debug(f"Skipping season number {info.season_id}...")
            continue

        season = series.get_season(info.season_id)
        typer.echo(f"Downloading {season.title}")
        season.download_images(download_dir / series.dirname)

        directory = download_dir / series.dirname / season.dirname
        with typer.progressbar(season.episodes) as episodes:
            for episode_number, program_id in enumerate(episodes, start=1):

                # If we're asked to only download one episode, possibly skip this one.
                # If it's a sequential series, only_episode_id is an episode number.
                # Otherwise, only_episode_id is a program_id.
                if only_episode_id is not None:
                    if (series.type == TVSeriesType.sequential) and (
                        only_episode_id != str(episode_number)
                    ):
                        logger.debug(f"Skipping episode number {episode_number}...")
                        continue
                    elif (
                        (series.type == TVSeriesType.news)
                        or (series.type == TVSeriesType.standard)
                    ) and (only_episode_id != program_id):
                        logger.debug(f"Skipping episode ID {program_id}...")
                        continue

                try:
                    program = TVProgram.from_program_id(program_id)
                except NotPlayableError as e:
                    typer.echo(f"Skipping: {e}")
                    continue

                if series.type == TVSeriesType.sequential:
                    sequence_string = f"s{season.season_id:>02s}e{episode_number:>02d}"
                else:
                    sequence_string = season.season_id

                program.download_as_episode(
                    valid_filename(series.title), sequence_string, directory
                )
                # typer.echo(f"Downloading episode {program.title}")


def download_program(download_dir: Path, program_id: str) -> None:
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
