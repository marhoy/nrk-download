import logging
import os.path
import re
import sys
import tempfile

import requests
import requests_cache

try:
    # Python 3
    from urllib.parse import quote, unquote
except ImportError:  # pragma: no cover
    # Python 2
    from urllib import quote, unquote  # noqa: F401


# Module wide logger
LOG = logging.getLogger(__name__)

# Use a local, persistent cache for the API requests
cache_file = os.path.join(
    tempfile.gettempdir(),
    "nrkdownload_cache_py{}{}".format(sys.version_info.major, sys.version_info.minor),
)
requests_cache.install_cache(cache_name=cache_file, backend="sqlite", expire_after=900)


def _api_url(path):
    # API Documentation:
    # https://psapi.nrk.no/
    # https://stsnapshottestwe.blob.core.windows.net/apidocumentation/documentation.html

    # This is the Granitt API: Nrk.Programspiller.Backend.WebAPI
    # http://v8.psapi.nrk.no  Now requires a key
    # granitt_url = 'http://nrkpswebapi2ne.cloudapp.net'
    granitt_url = "http://psapi-granitt-prod-we.cloudapp.net"

    # This is the Snapshot API: Nrk.PsApi
    # snapshot_url = "http://psapi3-webapp-prod-we.azurewebsites.net"

    # TV catalog API, documented here:
    # https://psapi.nrk.no/documentation/redoc/programsider-tv/
    psapi_tv_catalog = "https://psapi.nrk.no/tv/catalog"

    # Radio catalog API, documented here:
    # https://psapi.nrk.no/documentation/redoc/programsider-radio/
    psapi_radio_catalog = "https://psapi.nrk.no"

    if path.startswith("/mediaelement"):
        base_url = granitt_url
    elif path.startswith("/series"):
        base_url = psapi_tv_catalog
    elif path.startswith("/radio"):
        base_url = psapi_radio_catalog
    else:  # pragma: no cover
        LOG.error("No baseurl defined for %s", path)
        sys.exit(1)
    return base_url + path


def get_mediaelement(element_id):
    """
    Get information about an element ID

    :param element_id: The elementid you want information on
    :return: A dictionary with the JSON information
    """
    LOG.debug("Getting json-data on media element %s", element_id)
    r = requests.get(_api_url("/mediaelement/{:s}".format(element_id)))
    r.raise_for_status()
    json = r.json()

    # Extract download URLs for media and subtitles
    json["media_urls"] = []
    json["subtitle_urls"] = []
    if json.get("mediaAssets", None):
        for media in json.get("mediaAssets"):
            url = media.get("url", None)
            subtitle_url = media.get("webVttSubtitlesUrl", None)

            if url:
                # Download URL starts with /i instead of /z,
                # and has master.m3u8 at the end
                url = re.sub(r"\.net/z/", ".net/i/", url)
                url = re.sub(r"manifest\.f4m$", "master.m3u8", url)
                json["media_urls"].append(url)
            if subtitle_url:
                # ffmpeg struggles with downloading from https URLs
                subtitle_url = unquote(subtitle_url)
                subtitle_url = re.sub(r"^https", "http", subtitle_url)
                json["subtitle_urls"].append(subtitle_url)

    return json


def get_series(series_id):
    """
    Get information on a TV-series

    :param series_id: str
    :return: json
    """
    LOG.debug("Getting json-data on series %s", series_id)
    r = requests.get(_api_url("/series/{:s}".format(series_id)))
    r.raise_for_status()
    json = r.json()
    return json


def get_episode_ids_of_series_season(series_id, season_id):
    LOG.info(
        "Getting json-data with episode ids of series %s, season %s",
        series_id,
        season_id,
    )
    r = requests.get(_api_url("/series/{}/seasons/{}".format(series_id, season_id)))
    r.raise_for_status()
    json = r.json()

    if json["seriesType"] == "sequential":
        episodes = json["_embedded"]["episodes"]
    elif json["seriesType"] in ("standard", "news"):
        episodes = json["_embedded"]["instalments"]
    else:
        raise ValueError("Unkown series type: %s", json["seriesType"])

    episode_ids = [episode["prfId"] for episode in episodes]
    return episode_ids


def get_podcast_series(podcast_id):
    LOG.debug("Getting json-data of podcast series %s", podcast_id)
    r = requests.get(_api_url("/radio/catalog/podcast/{}".format(podcast_id)))
    r.raise_for_status()
    json = r.json()
    return json


def get_podcast_episodes(podcast_id):
    LOG.debug("Getting json-data for all episodes of podcast %s", podcast_id)
    params = {"pageSize": 20}
    r = requests.get(
        _api_url("/radio/catalog/podcast/{}/episodes/".format(podcast_id)),
        params=params,
    )
    r.raise_for_status()
    json = r.json()
    return json


def get_podcast_episode(podcast_id, episode_id):
    LOG.debug(
        "Getting json-data of podcast series %s: episode %s", episode_id, podcast_id
    )
    r = requests.get(
        _api_url("/podcasts/{}/episodes/{}".format(podcast_id, episode_id))
    )
    r.raise_for_status()
    json = r.json()
    return json
