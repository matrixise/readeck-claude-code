# src/readeck_cli/config.py
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

import tomli_w
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".config" / "readeck"
CONFIG_FILE = CONFIG_DIR / "config.toml"


class Config(BaseModel):
    url: str
    token: str


def load_config(
    url: str | None = None,
    token: str | None = None,
) -> Config:
    resolved_url = url or os.environ.get("READECK_URL")
    resolved_token = token or os.environ.get("READECK_TOKEN")

    if not resolved_url or not resolved_token:
        file_data = _read_config_file()
        section = file_data.get("default", {})
        resolved_url = resolved_url or section.get("url")
        resolved_token = resolved_token or section.get("token")

    if not resolved_url:
        raise ValueError(
            "No Readeck URL configured. "
            "Set READECK_URL or run 'readeck-cli auth login'."
        )
    if not resolved_token:
        raise ValueError(
            "No token configured. Set READECK_TOKEN or run 'readeck-cli auth login'."
        )

    return Config(url=resolved_url, token=resolved_token)


def save_config(url: str, token: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    existing = _read_config_file()
    existing.setdefault("default", {})
    existing["default"]["url"] = url
    existing["default"]["token"] = token
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(existing, f)


def remove_token() -> None:
    if not CONFIG_FILE.exists():
        return
    data = _read_config_file()
    data.get("default", {}).pop("token", None)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)


def _read_config_file() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)
