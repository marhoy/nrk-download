from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

import requests
from pydantic import BaseModel, HttpUrl

PS_API = "https://psapi.nrk.no/"
session = requests.Session()

# Create a generic variable that can be 'Season', or any subclass.
SeasonT = TypeVar("SeasonT", bound="Season")
# Create a generic variable that can be 'Series', or any subclass.
SeriesT = TypeVar("SeriesT", bound="Series")


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


class SeasonInfo(BaseModel):
    season_id: str
    title: str


class SeriesType(str, Enum):
    sequential = "sequential"
    standard = "standard"
    news = "news"


class Season(BaseModel):
    season_id: str
    title: str
    series_type: SeriesType
    poster_url: Optional[HttpUrl]
    episodes: List[str]

    @property
    def dirname(self) -> Path:
        if self.series_type == SeriesType.sequential:
            return Path(f"Season {int(self.season_id):02d}")
        return Path(f"Season {self.season_id}")

    @classmethod
    def get_json_data(cls, series_id: str, season_id: str) -> Dict[str, Any]:
        return NotImplemented

    @classmethod
    def from_ids(cls: Type[SeasonT], series_id: str, season_id: str) -> SeasonT:
        data = cls.get_json_data(series_id, season_id)

        if data.get("type"):
            # For Podcasts
            episodes = [
                episode["episodeId"]
                for episode in data["_embedded"]["episodes"]["_embedded"]["episodes"]
            ]
        else:
            # For TV-series
            episodes_name = "episodes"
            if data["seriesType"] in ("news", "standard"):
                episodes_name = "instalments"
            episodes = [
                episode["prfId"] for episode in data["_embedded"][episodes_name]
            ]

        return cls(
            season_id=season_id,
            title=data["titles"]["title"],
            series_type=data["seriesType"],
            poster_url=get_image_url(data, "posterImage"),
            episodes=episodes,
        )

    def download_images(self, basedir: Path) -> None:
        directory = basedir / self.dirname
        download_image_url(
            self.poster_url, directory / f"Season{self.season_id:>02s}.jpg"
        )


class Series(BaseModel):
    series_id: str
    title: str
    type: SeriesType
    season_info: List[SeasonInfo]
    image_url: Optional[HttpUrl]
    poster_url: Optional[HttpUrl]
    backdrop_url: Optional[HttpUrl]
    square_image_url: Optional[HttpUrl]

    def get_season(self, season_id: str) -> Season:
        """To be implemented by subclass."""
        return NotImplemented

    @classmethod
    def get_json_data(cls, id: str) -> Dict[str, Any]:
        """To be implemented by subclass."""
        return NotImplemented

    @property
    def dirname(self) -> Path:
        return Path(valid_filename(self.title))

    @classmethod
    def from_series_id(cls: Type[SeriesT], series_id: str) -> SeriesT:
        data = cls.get_json_data(series_id)

        if data.get("series"):
            # For Podcasts
            detail_key = "series"
        else:
            # For TV-series
            detail_key = data["seriesType"]

        return cls(
            series_id=series_id,
            title=data[detail_key]["titles"]["title"],
            type=data["seriesType"],
            season_info=[
                SeasonInfo(season_id=item["name"], title=item["title"])
                for item in data["_links"]["seasons"]
            ],
            image_url=get_image_url(data[detail_key], "image"),
            poster_url=get_image_url(data[detail_key], "posterImage"),
            backdrop_url=get_image_url(data[detail_key], "backdropImage"),
            square_image_url=get_image_url(data[detail_key], "squareImage"),
        )

    def download_images(self, basedir: Path) -> None:
        directory = basedir / self.dirname
        download_image_url(self.poster_url, directory / "poster.jpg")
        download_image_url(self.backdrop_url, directory / "backdrop.jpg")
        download_image_url(self.image_url, directory / "banner.jpg")
        download_image_url(self.square_image_url, directory / "cover.jpg")
