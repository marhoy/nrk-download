from typing import Any, Dict

from nrkdownload.nrk_common import PS_API, Season, Series, session


class PodcastSeason(Season):
    @classmethod
    def get_json_data(cls, series_id: str, season_id: str) -> Dict[str, Any]:
        r = session.get(
            PS_API + f"/radio/catalog/podcast/{series_id}/seasons/{season_id}"
        )
        r.raise_for_status()
        return r.json()


class Podcast(Series):
    def get_season(self, season_id: str) -> Season:
        return PodcastSeason.from_ids(self.series_id, season_id)

    @classmethod
    def get_json_data(cls, podcast_id: str) -> Dict[str, Any]:
        r = session.get(PS_API + f"/radio/catalog/podcast/{podcast_id}")
        r.raise_for_status()
        return r.json()
