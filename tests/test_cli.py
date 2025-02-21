"""Tests for the CLI."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from nrkdownload.cli import app

runner = CliRunner()


def test_version_string() -> None:  # noqa: D103
    result = runner.invoke(
        app,
        ["--version"],
    )
    assert result.exit_code == 0
    assert "version" in result.stdout


def test_verbose_level() -> None:  # noqa: D103
    result = runner.invoke(app, ["-v"])
    assert "Setting loglevel to SUCCESS" in result.stdout
    result = runner.invoke(app, ["-vv"])
    assert "Setting loglevel to INFO" in result.stdout
    result = runner.invoke(app, ["-vvv"])
    assert "Setting loglevel to DEBUG" in result.stdout
    result = runner.invoke(app, ["-vvvv"])
    assert "Setting loglevel to TRACE" in result.stdout


def test_illegal_url() -> None:  # noqa: D103
    result = runner.invoke(app, "https://tv.nrk.no/")
    assert result.exit_code == 1


def test_not_available_program(tmp_path: Path) -> None:  # noqa: D103
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/program/KOID28004110",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert "not playable" in result.stdout


def test_not_available_episode(tmp_path: Path) -> None:  # noqa: D103
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/elias/sesong/1/episode/MSUE10001112",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert "not playable" in result.stdout


def test_ffmpeg_not_found(tmp_path: Path) -> None:  # noqa: D103
    # Change $PATH environment variable to make ffmpeg not found
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/elias/sesong/1/episode/MSUE10001112",
            "--download-dir",
            str(tmp_path),
        ],
        env={"PATH": ""},
    )
    assert "FFmpeg not found" in result.stdout


@pytest.mark.download
def test_download_sequential_episode(tmp_path: Path) -> None:  # noqa: D103
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/humorkalender/sesong/1/episode/MUHH54000115",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    directory = tmp_path / "Humorkalender"
    assert (directory / "banner.jpg").exists()
    directory = directory / "Season 01"
    assert (
        directory / "Humorkalender - s01e01 - 1. Christian Kopperuds julenissetips.jpg"
    ).exists()
    assert (
        directory / "Humorkalender - s01e01 - 1. Christian Kopperuds julenissetips.m4v"
    ).exists()
    assert (
        directory
        / "Humorkalender - s01e01 - 1. Christian Kopperuds julenissetips.no.srt"
    ).exists()


@pytest.mark.download
def test_download_extramaterial(tmp_path: Path) -> None:  # noqa: D103
    # Download the same video twice, to trigger the "already exists" line
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/monsen-og-nasjonalparkene/sesong/ekstramateriale/episode/KMNO10002125",
            "https://tv.nrk.no/serie/monsen-og-nasjonalparkene/sesong/ekstramateriale/episode/KMNO10002125",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    directory = tmp_path / "Monsen og nasjonalparkene"
    assert (directory / "banner.jpg").exists()
    directory = directory / "Ekstramateriale"
    assert (
        directory / "Monsen og nasjonalparkene - TRAILER Monsen og nasjonalparkene.jpg"
    ).exists()
    assert (
        directory / "Monsen og nasjonalparkene - TRAILER Monsen og nasjonalparkene.m4v"
    ).exists()
    assert (
        directory
        / "Monsen og nasjonalparkene - TRAILER Monsen og nasjonalparkene.no.srt"
    ).exists()


@pytest.mark.download
def test_download_news_episode(tmp_path: Path) -> None:  # noqa: D103
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/distriktsnyheter-oslo-og-viken/sesong/202204/episode/DKOV98040122",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    directory = tmp_path / "Distriktsnyheter Oslo og Viken"
    assert (directory / "banner.jpg").exists()
    assert (directory / "backdrop.jpg").exists()
    directory = directory / "Season 202204"
    assert (
        directory / "Distriktsnyheter Oslo og Viken - 202204 - 1. april 2022.jpg"
    ).exists()
    assert (
        directory / "Distriktsnyheter Oslo og Viken - 202204 - 1. april 2022.m4v"
    ).exists()
    assert (
        directory / "Distriktsnyheter Oslo og Viken - 202204 - 1. april 2022.no.srt"
    ).exists()


@pytest.mark.download
def test_download_program(tmp_path: Path) -> None:  # noqa: D103
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/program/KMNO02000115",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    directory = tmp_path / "Dokumentaren om Radioresepsjonen"
    assert (directory / "Dokumentaren om Radioresepsjonen (2010).jpg").exists()
    assert (directory / "Dokumentaren om Radioresepsjonen (2010).m4v").exists()
