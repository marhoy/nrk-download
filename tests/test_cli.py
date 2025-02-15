from pathlib import Path

from typer.testing import CliRunner

from nrkdownload.cli import app

runner = CliRunner()


def test_version_string() -> None:
    result = runner.invoke(
        app,
        ["--version"],
    )
    assert result.exit_code == 0
    assert "version" in result.stdout


def test_verbose_level() -> None:
    result = runner.invoke(app, ["-v", "--version"])
    assert "Setting loglevel to SUCCESS" in result.stdout
    result = runner.invoke(app, ["-vv", "--version"])
    assert "Setting loglevel to INFO" in result.stdout
    result = runner.invoke(app, ["-vvv", "--version"])
    assert "Setting loglevel to DEBUG" in result.stdout
    result = runner.invoke(app, ["-vvvv", "--version"])
    assert "Setting loglevel to TRACE" in result.stdout


def test_illegal_url() -> None:
    result = runner.invoke(app, "https://tv.nrk.no/")
    assert result.exit_code == 1


def test_not_available_program(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/program/KOID28004110",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert "not playable" in result.stdout


def test_not_available_episode(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/elias/sesong/1/episode/1/avspiller--download-dir",
            str(tmp_path),
        ],
    )
    assert "not playable" in result.stdout


def test_download_sequential_episode(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/kongen-av-gulset/sesong/1/episode/3/avspiller",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    dir = tmp_path / "Kongen av Gulset"
    assert (dir / "banner.jpg").exists()
    dir = dir / "Season 01"
    assert (
        dir / "Kongen av Gulset - s01e03 - 3. Pene jenter, peacocking & pine.jpg"
    ).exists()
    assert (
        dir / "Kongen av Gulset - s01e03 - 3. Pene jenter, peacocking & pine.m4v"
    ).exists()
    assert (
        dir / "Kongen av Gulset - s01e03 - 3. Pene jenter, peacocking & pine.no.srt"
    ).exists()


def test_download_news_episode(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/serie/distriktsnyheter-oslo-og-viken/202204/DKOV98040122/avspiller",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    dir = tmp_path / "Distriktsnyheter Oslo og Viken"
    assert (dir / "banner.jpg").exists()
    assert (dir / "backdrop.jpg").exists()
    dir = dir / "Season 202204"
    assert (dir / "Distriktsnyheter Oslo og Viken - 202204 - 1. april.jpg").exists()
    assert (dir / "Distriktsnyheter Oslo og Viken - 202204 - 1. april.m4v").exists()
    assert (dir / "Distriktsnyheter Oslo og Viken - 202204 - 1. april.no.srt").exists()


def test_download_program(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "https://tv.nrk.no/program/KMNO02000115",
            "--download-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    dir = tmp_path / "Dokumentaren om Radioresepsjonen"
    assert (dir / "Dokumentaren om Radioresepsjonen (2010).jpg").exists()
    assert (dir / "Dokumentaren om Radioresepsjonen (2010).m4v").exists()
