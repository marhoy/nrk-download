from nrkdownload.nrk_tv import TVProgram, TVSeries


def test_tv_series() -> None:
    series = TVSeries.from_series_id("kongen-av-gulset")
    assert series.title == "Kongen av Gulset"
    assert len(series.season_info) == 2


def test_tv_season() -> None:
    series = TVSeries.from_series_id("kongen-av-gulset")
    season = series.get_season(series.season_info[0].season_id)
    assert len(season.episodes) == 7


def test_tv_program() -> None:
    program = TVProgram.from_program_id("MSUI14009516")
    assert program.title == "Røverrotta"
