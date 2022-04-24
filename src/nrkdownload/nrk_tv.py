from __future__ import annotations

import datetime
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import ffmpeg
import requests
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

PS_API = "https://psapi.nrk.no/"
session = requests.Session()


class NotPlayableError(Exception):
    pass


def valid_filename(string: str) -> str:
    filename = re.sub(r'[/\\?<>:*|!"\']', "", string)
    return filename


def get_image_url(data: Dict[str, Any], key: str) -> Optional[HttpUrl]:
    if data.get(key):
        return data[key][-1]["url"]
    return None


def download_image_url(url: Optional[HttpUrl], filename: Path) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    if not filename.exists() and url is not None:
        with open(filename, "wb") as file:
            file.write(requests.get(url).content)


class TVProgram(BaseModel):
    """Class for TV programs.

    Example:
    >>> program = TVProgram.from_program_id("NNFA19010122")
    """

    program_id: str = Field(..., regex=r"^[A-Z]{4}\d{8}$")
    title: str
    prod_year: int
    duration: datetime.timedelta
    image_url: Optional[HttpUrl]
    poster_url: Optional[HttpUrl]
    backdrop_url: Optional[HttpUrl]
    media_urls: List[HttpUrl]
    subtitle_urls: List[HttpUrl]

    @classmethod
    def from_program_id(cls, program_id: str) -> TVProgram:
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
                title["webVtt"] for title in manifest["playable"]["subtitles"]
            ],
        )

    def download_as_program(self, basedir: Path) -> None:
        filename = basedir / f"{self.title} ({self.prod_year})"
        download_image_url(self.poster_url, basedir / "poster.jpg")
        download_image_url(self.backdrop_url, basedir / f"{filename}-backdrop.jpg")
        download_image_url(self.image_url, basedir / f"{filename}.jpg")
        download_video(self, filename)

    def download_as_episode(
        self, series_title: str, sequence_string: str, basedir: Path
    ) -> None:
        filename = basedir / f"{series_title} - {sequence_string} - {self.title}"
        download_image_url(self.image_url, Path(f"{filename}.jpg"))
        download_video(self, filename)


class TVSeriesType(str, Enum):
    sequential = "sequential"
    standard = "standard"
    news = "news"


class SeasonInfo(BaseModel):
    season_id: str
    title: str


class Season(BaseModel):
    season_id: str
    title: str
    series_type: TVSeriesType
    poster_url: Optional[HttpUrl]
    episodes: List[str]

    @property
    def dirname(self) -> Path:
        if self.series_type == TVSeriesType.sequential:
            return Path(f"Season {int(self.season_id):02d}")
        return Path(f"Season {self.season_id}")

    @classmethod
    def from_ids(cls, series_id: str, season_id: str) -> Season:
        r = session.get(PS_API + f"/tv/catalog/series/{series_id}/seasons/{season_id}")
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
        directory = basedir / self.dirname
        download_image_url(
            self.poster_url, directory / f"Season{self.season_id:>02s}.jpg"
        )


class TVSeries(BaseModel):
    series_id: str
    title: str
    type: TVSeriesType
    season_info: List[SeasonInfo]
    image_url: Optional[HttpUrl]
    poster_url: Optional[HttpUrl]
    backdrop_url: Optional[HttpUrl]

    def get_season(self, season_id: str) -> Season:
        return Season.from_ids(self.series_id, season_id)

    @property
    def dirname(self) -> Path:
        return Path(valid_filename(self.title))

    @classmethod
    def from_series_id(cls, series_id: str) -> TVSeries:
        r = session.get(PS_API + f"/tv/catalog/series/{series_id}")
        r.raise_for_status()
        data = r.json()

        return cls(
            series_id=series_id,
            title=data[data["seriesType"]]["titles"]["title"],
            type=data["seriesType"],
            season_info=[
                SeasonInfo(season_id=item["name"], title=item["title"])
                for item in data["_links"]["seasons"]
            ],
            image_url=get_image_url(data[data["seriesType"]], "image"),
            poster_url=get_image_url(data[data["seriesType"]], "posterImage"),
            backdrop_url=get_image_url(data[data["seriesType"]], "backdropImage"),
        )

    def download_images(self, basedir: Path) -> None:
        directory = basedir / self.dirname
        download_image_url(self.poster_url, directory / "poster.jpg")
        download_image_url(self.backdrop_url, directory / "backdrop.jpg")
        download_image_url(self.image_url, directory / "banner.jpg")


def download_video(program: TVProgram, filename: Path) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)

    # TODO: Handle programs with multiple subtitle URLs
    subtitle_filename = Path(f"{filename}.no.srt")
    if program.subtitle_urls and not subtitle_filename.exists():
        logger.info("Downloading subtitles")
        out, err = (
            ffmpeg.input(program.subtitle_urls[0])
            .output(str(subtitle_filename))
            .run(quiet=True)
        )
        logger.success("Downloaded subtitles")
        logger.trace(err.decode("utf-8"))

    # TODO: Handle programs with multiple media URLs
    media_filename = Path(f"{filename}.m4v")
    if not media_filename.exists():
        logger.info("Downloading media files")
        out, err = (
            ffmpeg.input(program.media_urls[0])
            .output(str(media_filename), vcodec="copy", acodec="copy")
            .run(quiet=True)
        )
        logger.success("Downloaded media files")
        logger.trace(err.decode("utf-8"))
