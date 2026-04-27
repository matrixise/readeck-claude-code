# tests/unit/test_config.py
import os
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest
import tomli_w

from readeck_cli.config import load_config, remove_token, save_config


def test_load_config_from_env(tmp_path: Path) -> None:
    with patch.dict(
        os.environ,
        {"READECK_URL": "https://test.example.com", "READECK_TOKEN": "tok123"},
    ):
        with patch("readeck_cli.config.CONFIG_FILE", tmp_path / "config.toml"):
            config = load_config()
    assert config.url == "https://test.example.com"
    assert config.token == "tok123"


def test_load_config_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        tomli_w.dumps(
            {"default": {"url": "https://file.example.com", "token": "filetoken"}}
        ),
        encoding="utf-8",
    )
    with patch.dict(os.environ, {}, clear=True):
        with patch("readeck_cli.config.CONFIG_FILE", config_file):
            config = load_config()
    assert config.url == "https://file.example.com"
    assert config.token == "filetoken"


def test_env_takes_precedence_over_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        tomli_w.dumps(
            {"default": {"url": "https://file.example.com", "token": "filetoken"}}
        )
    )
    with patch.dict(
        os.environ,
        {"READECK_URL": "https://env.example.com", "READECK_TOKEN": "envtoken"},
    ):
        with patch("readeck_cli.config.CONFIG_FILE", config_file):
            config = load_config()
    assert config.url == "https://env.example.com"
    assert config.token == "envtoken"


def test_cli_flags_take_precedence_over_env(tmp_path: Path) -> None:
    with patch.dict(
        os.environ,
        {"READECK_URL": "https://env.example.com", "READECK_TOKEN": "envtoken"},
    ):
        with patch("readeck_cli.config.CONFIG_FILE", tmp_path / "config.toml"):
            config = load_config(url="https://flag.example.com", token="flagtoken")
    assert config.url == "https://flag.example.com"
    assert config.token == "flagtoken"


def test_load_config_raises_when_nothing_configured(tmp_path: Path) -> None:
    with patch.dict(os.environ, {}, clear=True):
        with patch("readeck_cli.config.CONFIG_FILE", tmp_path / "missing.toml"):
            with pytest.raises(ValueError, match="No Readeck URL"):
                load_config()


def test_save_config_writes_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    with patch("readeck_cli.config.CONFIG_DIR", tmp_path):
        with patch("readeck_cli.config.CONFIG_FILE", config_file):
            save_config(url="https://saved.example.com", token="savedtoken")
    data = tomllib.loads(config_file.read_text())
    assert data["default"]["url"] == "https://saved.example.com"
    assert data["default"]["token"] == "savedtoken"


def test_remove_token_clears_token(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        tomli_w.dumps({"default": {"url": "https://x.com", "token": "abc"}})
    )
    with patch("readeck_cli.config.CONFIG_FILE", config_file):
        remove_token()
    data = tomllib.loads(config_file.read_text())
    assert "token" not in data.get("default", {})
