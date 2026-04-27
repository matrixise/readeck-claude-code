# tests/unit/test_main.py
from typer.testing import CliRunner

from readeck_cli.main import app

runner = CliRunner()


def test_app_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_auth_subcommand_exists() -> None:
    result = runner.invoke(app, ["auth", "--help"])
    assert result.exit_code == 0


def test_bookmarks_subcommand_exists() -> None:
    result = runner.invoke(app, ["bookmarks", "--help"])
    assert result.exit_code == 0


def test_labels_subcommand_exists() -> None:
    result = runner.invoke(app, ["labels", "--help"])
    assert result.exit_code == 0


def test_collections_subcommand_exists() -> None:
    result = runner.invoke(app, ["collections", "--help"])
    assert result.exit_code == 0


def test_highlights_subcommand_exists() -> None:
    result = runner.invoke(app, ["highlights", "--help"])
    assert result.exit_code == 0


def test_profile_subcommand_exists() -> None:
    result = runner.invoke(app, ["profile", "--help"])
    assert result.exit_code == 0
