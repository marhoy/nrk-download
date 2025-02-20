"""Tests for the URL matching functions in nrkdownload.cli."""

from nrkdownload.cli import match_program_url, match_series_url


def test_match_program_url() -> None:  # noqa: D103
    # Example program URL:
    # https://tv.nrk.no/program/KOID75000320
    match = match_program_url("https://tv.nrk.no/program/KOID75000320")
    assert match == "KOID75000320"
    match = match_program_url("https://tv.nrk.no/KOID75000320")
    assert match is None


def test_match_no_series_url() -> None:  # noqa: D103
    assert match_series_url("https://tv.nrk.no/") is None


def test_match_sequential_series_url() -> None:  # noqa: D103
    # Example "standard" series URL:
    # https://tv.nrk.no/serie/klassequizen
    # https://tv.nrk.no/serie/klassequizen/2021
    # https://tv.nrk.no/serie/klassequizen/2021/DSRR21000521/avspiller

    # A sequential series
    match = match_series_url("https://tv.nrk.no/serie/kongen-av-gulset")
    assert match == ("kongen-av-gulset", None, None)
    match = match_series_url("https://tv.nrk.no/serie/kongen-av-gulset/sesong/1")
    assert match == ("kongen-av-gulset", "1", None)
    match = match_series_url(
        "https://tv.nrk.no/serie/kongen-av-gulset/sesong/1/episode/3"
    )
    assert match == ("kongen-av-gulset", "1", "3")
    match = match_series_url(
        "https://tv.nrk.no/serie/kongen-av-gulset/sesong/1/episode/3/avspiller"
    )
    assert match == ("kongen-av-gulset", "1", "3")


def test_match_news_series_url() -> None:  # noqa: D103
    # A news series
    match = match_series_url("https://tv.nrk.no/serie/dagsrevyen-21")
    assert match == ("dagsrevyen-21", None, None)
    match = match_series_url("https://tv.nrk.no/serie/dagsrevyen-21/202203")
    assert match == ("dagsrevyen-21", "202203", None)
    match = match_series_url(
        "https://tv.nrk.no/serie/dagsrevyen-21/202203/NNFA21030122/avspiller"
    )
    assert match == ("dagsrevyen-21", "202203", "NNFA21030122")
