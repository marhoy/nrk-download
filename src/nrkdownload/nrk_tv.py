from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import ffmpeg
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

from nrkdownload.nrk_common import (
    PS_API,
    NotPlayableError,
    Season,
    Series,
    download_image_url,
    get_image_url,
    session,
    valid_filename,
)


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


class TVSeason(Season):
    @classmethod
    def get_json_data(cls, series_id: str, season_id: str) -> Dict[str, Any]:
        r = session.get(PS_API + f"/tv/catalog/series/{series_id}/seasons/{season_id}")
        r.raise_for_status()
        return r.json()


class TVSeries(Series):
    def get_season(self, season_id: str) -> TVSeason:
        return TVSeason.from_ids(self.series_id, season_id)

    @classmethod
    def get_json_data(cls, series_id: str) -> Dict[str, Any]:
        r = session.get(PS_API + f"/tv/catalog/series/{series_id}")
        r.raise_for_status()
        return r.json()


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
