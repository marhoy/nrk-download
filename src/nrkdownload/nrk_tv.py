"""Functions for reading from the NRK TV API."""

from __future__ import annotations

import datetime
import re
from enum import Enum
from pathlib import Path
from typing import Any

import requests
import rich.progress
from ffmpeg import FFmpeg, Progress
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

PS_API = "https://psapi.nrk.no/"
session = requests.Session()


class NotPlayableError(Exception):
    """Raised when a program is not playable."""

    pass


def valid_filename(string: str) -> str:
    """Convert a string to a valid filename."""
    return re.sub(r'[/\\?<>:*|!"\']', "", string)


def get_image_url(data: dict[str, Any], key: str) -> HttpUrl | None:
    """Get the URL of an image from a dictionary."""
    if data.get(key):
        return data[key][-1]["url"]
    return None


def download_image_url(url: HttpUrl | None, filename: Path) -> None:
    """Download an image from a URL."""
    if url is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        if not filename.exists():
            filename.write_bytes(requests.get(url.unicode_string(), timeout=5).content)


class TVProgram(BaseModel):
    """Class for TV programs.

    Example:
    >>> program = TVProgram.from_program_id("NNFA19010122")
    """

    program_id: str = Field(..., pattern=r"^[A-Z]{4}\d{8}$")
    title: str
    prod_year: int
    duration: datetime.timedelta
    image_url: HttpUrl | None
    poster_url: HttpUrl | None
    backdrop_url: HttpUrl | None
    media_urls: list[HttpUrl]
    subtitle_urls: list[HttpUrl]

    @classmethod
    def from_program_id(cls, program_id: str) -> TVProgram:
        """Create a TVProgram object from a program ID."""
        r = session.get(PS_API + f"/tv/catalog/programs/{program_id}")
        r.raise_for_status()
        data = r.json()
        r = session.get(PS_API + f"/playback/manifest/program/{program_id}")
        r.raise_for_status()
        manifest = r.json()

        title = valid_filename(data["programInformation"]["titles"]["title"])
        if manifest["playability"] != "playable":
            raise NotPlayableError(f'Program "{title}" ({program_id}) is not playable')
        prod_year = data["moreInformation"]["productionYear"]
        return cls(
            program_id=program_id,
            title=title,
            prod_year=prod_year,
            duration=datetime.timedelta(
                seconds=data["moreInformation"]["duration"]["seconds"]
            ),
            image_url=get_image_url(data["programInformation"], "image"),
            poster_url=get_image_url(data, "posterImage"),
            backdrop_url=get_image_url(data, "backdropImage"),
            media_urls=[asset["url"] for asset in manifest["playable"]["assets"]],
            subtitle_urls=[
                title["webVtt"]
                for title in manifest["playable"]["subtitles"]
                if title["defaultOn"]
            ],
        )

    def download_as_program(self, basedir: Path) -> None:
        """Download as a standalone program (not part of a series)."""
        filename = basedir / f"{self.title} ({self.prod_year})"
        download_image_url(self.poster_url, basedir / "poster.jpg")
        download_image_url(self.backdrop_url, basedir / f"{filename}-backdrop.jpg")
        download_image_url(self.image_url, basedir / f"{filename}.jpg")
        download_video(self, filename)

    def download_as_episode(
        self, series_title: str, sequence_string: str, basedir: Path
    ) -> None:
        """Download as an episode in a series."""
        if not sequence_string:
            filename = basedir / f"{series_title} - {self.title}"
        else:
            filename = basedir / f"{series_title} - {sequence_string} - {self.title}"
        download_image_url(self.image_url, Path(f"{filename}.jpg"))
        download_video(self, filename)


class TVSeriesType(str, Enum):
    """Enum for TV series types."""

    sequential = "sequential"
    standard = "standard"
    news = "news"


class SeasonInfo(BaseModel):
    """Information about a season."""

    season_id: str
    title: str


class Season(BaseModel):
    """Class for TV series seasons."""

    season_id: str
    title: str
    series_type: TVSeriesType
    poster_url: HttpUrl | None
    episodes: list[str]

    @property
    def dirname(self) -> Path:
        """Get the directory name for the season."""
        if self.series_type == TVSeriesType.sequential:
            if self.season_id == "ekstramateriale":
                return Path("Ekstramateriale")
            return Path(f"Season {int(self.season_id):02d}")
        return Path(f"Season {self.season_id}")

    @classmethod
    def from_ids(cls, series_id: str, season_id: str) -> Season:
        """Create a Season object from a series ID and season ID."""
        if season_id == "ekstramateriale":
            r = session.get(PS_API + f"/tv/catalog/series/{series_id}/extramaterial")
        else:
            r = session.get(
                PS_API + f"/tv/catalog/series/{series_id}/seasons/{season_id}"
            )
        r.raise_for_status()
        data = r.json()

        episodes_name = "episodes"
        if data["seriesType"] in ("news", "standard"):
            episodes_name = "instalments"

        return cls(
            season_id=season_id,
            title=data["titles"]["title"],
            series_type=data["seriesType"],
            poster_url=get_image_url(data, "posterImage"),
            episodes=[episode["prfId"] for episode in data["_embedded"][episodes_name]],
        )

    def download_images(self, basedir: Path) -> None:
        """Download images for the season."""
        directory = basedir / self.dirname
        download_image_url(
            self.poster_url, directory / f"Season{self.season_id:>02s}.jpg"
        )


class TVSeries(BaseModel):
    """Class for TV series."""

    series_id: str
    title: str
    type: TVSeriesType
    season_info: list[SeasonInfo]
    extramaterial: SeasonInfo | None
    image_url: HttpUrl | None
    poster_url: HttpUrl | None
    backdrop_url: HttpUrl | None

    @property
    def season_infos(self) -> list[SeasonInfo]:
        """Get the season info, including the extramaterial."""
        return self.season_info + ([self.extramaterial] if self.extramaterial else [])

    def get_season(self, season_id: str) -> Season:
        """Get a season object from a season ID."""
        return Season.from_ids(self.series_id, season_id)

    @property
    def dirname(self) -> Path:
        """Get the directory name for the series."""
        return Path(valid_filename(self.title))

    @classmethod
    def from_series_id(cls, series_id: str, with_extras: bool = False) -> TVSeries:
        """Create a TVSeries object from a series ID."""
        r = session.get(PS_API + f"/tv/catalog/series/{series_id}")
        r.raise_for_status()
        data = r.json()

        # Possibly add an "Ekstramateriale" season
        extramaterial = None
        if with_extras and data["_links"].get("extramaterial"):
            extramaterial = SeasonInfo(
                season_id="ekstramateriale", title="Ekstramateriale"
            )

        return cls(
            series_id=series_id,
            title=data[data["seriesType"]]["titles"]["title"],
            type=data["seriesType"],
            season_info=[
                SeasonInfo(season_id=item["name"], title=item["title"])
                for item in data["_links"]["seasons"]
            ],
            extramaterial=extramaterial,
            image_url=get_image_url(data[data["seriesType"]], "image"),
            poster_url=get_image_url(data[data["seriesType"]], "posterImage"),
            backdrop_url=get_image_url(data[data["seriesType"]], "backdropImage"),
        )

    def download_images(self, basedir: Path) -> None:
        """Download images for the series."""
        directory = basedir / self.dirname
        download_image_url(self.poster_url, directory / "poster.jpg")
        download_image_url(self.backdrop_url, directory / "backdrop.jpg")
        download_image_url(self.image_url, directory / "banner.jpg")


def download_video(program: TVProgram, filename: Path) -> None:
    """Download subtitles and video files for a program."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    # TODO: Handle programs with multiple subtitle URLs
    subtitle_filename = Path(f"{filename}.no.srt")
    if program.subtitle_urls and not subtitle_filename.exists():
        logger.info("Downloading subtitles")

        ffmpeg = (
            FFmpeg()
            .input(program.subtitle_urls[0].unicode_string())
            .output(str(subtitle_filename))
        )

        ffmpeg.execute()
        logger.success("Downloaded subtitles")

    # TODO: Handle programs with multiple media URLs
    media_filename = Path(f"{filename}.m4v")
    if media_filename.exists():
        logger.info(f"Media file {media_filename} already downloaded")
        return

    with rich.progress.Progress() as rich_progress:
        logger.info("Downloading media files")
        task1 = rich_progress.add_task(
            f"[red]{program.title[:15]}", total=program.duration.total_seconds()
        )

        ffmpeg = (
            FFmpeg()
            .input(program.media_urls[0].unicode_string())
            .output(str(media_filename), vcodec="copy", acodec="copy")
        )

        @ffmpeg.on("progress")
        def on_progress(ffmpeg_progress: Progress) -> None:
            rich_progress.update(task1, completed=ffmpeg_progress.time.total_seconds())

        ffmpeg.execute()
        # Make sure the progress bar is at 100%
        rich_progress.update(task1, completed=program.duration.total_seconds())

    logger.success("Downloaded media files")
