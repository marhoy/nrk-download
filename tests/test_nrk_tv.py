"""Tests for the NRK TV API."""

from nrkdownload.nrk_tv import TVProgram, TVSeries, TVSeriesType


def test_tv_series() -> None:  # noqa: D103
    series = TVSeries.from_series_id("kongen-av-gulset")
    assert series.title == "Kongen av Gulset"
    assert len(series.season_info) == 2


def test_tv_season() -> None:  # noqa: D103
    series = TVSeries.from_series_id("kongen-av-gulset")
    season = series.get_season(series.season_info[0].season_id)
    assert len(season.episodes) == 7
    assert series.type == TVSeriesType.sequential


def test_tv_program() -> None:  # noqa: D103
    program = TVProgram.from_program_id("MYNR46000018")
    assert program.title == "Arif og Unge Ferrari med Stavanger Symfoniorkester"
