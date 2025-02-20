"""Functions for downloading TV programs and series from NRK TV."""

from __future__ import annotations

from pathlib import Path

import typer
from loguru import logger

from nrkdownload.nrk_tv import (
    NotPlayableError,
    TVProgram,
    TVSeries,
    TVSeriesType,
    valid_filename,
)


def download_series(
    download_dir: Path,
    series_id: str,
    only_season_id: str | None = None,
    only_episode_id: str | None = None,
) -> None:
    """Download a series.

    Args:
        download_dir (_type_): _description_
        series_id (_type_): _description_
        only_season_id (_type_, optional): _description_. Defaults to None.
        only_episode_id (_type_, optional): _description_. Defaults to None.
    """
    series = TVSeries.from_series_id(series_id)
    typer.echo(f"Downloading {series.title}")
    series.download_images(download_dir)
    for season_info in series.season_infos:
        if (only_season_id is not None) and (season_info.season_id != only_season_id):
            logger.debug(f"Skipping season number {season_info.season_id}...")
            continue

        season = series.get_season(season_info.season_id)
        typer.echo(f"Downloading {season.title}")
        season.download_images(download_dir / series.dirname)

        directory = download_dir / series.dirname / season.dirname
        for episode_number, program_id in enumerate(season.episodes, start=1):
            # If we're asked to only download one episode, possibly skip this one.
            if (only_episode_id is not None) and (only_episode_id != program_id):
                logger.debug(f"Skipping episode ID {program_id}...")
                continue

            try:
                program = TVProgram.from_program_id(program_id)
            except NotPlayableError as e:
                typer.echo(f"Skipping: {e}")
                continue

            if series.type == TVSeriesType.sequential:
                if season_info.season_id == "ekstramateriale":
                    sequence_string = ""
                else:
                    sequence_string = f"s{season.season_id:>02s}e{episode_number:>02d}"
            else:
                sequence_string = season.season_id

            program.download_as_episode(
                valid_filename(series.title), sequence_string, directory
            )
            # typer.echo(f"Downloading episode {program.title}")


def download_program(download_dir: Path, program_id: str) -> None:
    """Download a Program.

    Args:
        download_dir (_type_): _description_
        program_id (_type_): _description_
    """
    try:
        program = TVProgram.from_program_id(program_id)
    except NotPlayableError as e:
        typer.echo(f"Skipping: {e}")
        return
    typer.echo(f"Downloading {program.title}")
    program.download_as_program(download_dir / program.title)
