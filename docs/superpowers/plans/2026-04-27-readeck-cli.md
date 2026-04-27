# Readeck CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully-featured async CLI (`readeck-cli`) to interact with a self-hosted Readeck instance, covering auth, bookmarks, labels, collections, highlights, and profile.

**Architecture:** Three layers — `client/http.py` handles raw HTTPX calls, `services/` contains business logic per resource returning Pydantic models, `commands/` holds thin Typer wrappers. Config resolves from CLI flags → env vars → `~/.config/readeck/config.toml`.

**Tech Stack:** Python 3.13, uv, Typer, HTTPX (async), Pydantic v2, Rich, tomli-w, pytest + respx, ruff, mypy, ty, pre-commit, GitHub Actions.

---

## File Map

| File | Responsibility |
|---|---|
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `.gitignore` | Ignore `.claude/`, `.env`, build artifacts |
| `.pre-commit-config.yaml` | ruff check, ruff format, mypy, ty hooks |
| `.github/workflows/ci.yml` | lint + test jobs |
| `src/readeck_cli/__init__.py` | Package marker |
| `src/readeck_cli/main.py` | Typer app, registers all sub-apps |
| `src/readeck_cli/config.py` | Config loading: flags > env > TOML file |
| `src/readeck_cli/output.py` | Rich table / JSON rendering |
| `src/readeck_cli/client/__init__.py` | Package marker |
| `src/readeck_cli/client/http.py` | `ReadeckClient` (HTTPX async) + `ReadeckAPIError` |
| `src/readeck_cli/models/__init__.py` | Package marker |
| `src/readeck_cli/models/auth.py` | `TokenInfo` Pydantic model |
| `src/readeck_cli/models/bookmark.py` | `Bookmark`, `BookmarkResult` |
| `src/readeck_cli/models/label.py` | `Label` |
| `src/readeck_cli/models/collection.py` | `Collection` |
| `src/readeck_cli/models/highlight.py` | `Highlight` |
| `src/readeck_cli/models/profile.py` | `UserProfile` |
| `src/readeck_cli/services/__init__.py` | Package marker |
| `src/readeck_cli/services/auth.py` | `AuthService` |
| `src/readeck_cli/services/bookmarks.py` | `BookmarkService` |
| `src/readeck_cli/services/labels.py` | `LabelService` |
| `src/readeck_cli/services/collections.py` | `CollectionService` |
| `src/readeck_cli/services/highlights.py` | `HighlightService` |
| `src/readeck_cli/services/profile.py` | `ProfileService` |
| `src/readeck_cli/commands/__init__.py` | Package marker |
| `src/readeck_cli/commands/auth.py` | `auth login/logout/status/token set` |
| `src/readeck_cli/commands/bookmarks.py` | `bookmarks list/get/add/update/delete/search/export` |
| `src/readeck_cli/commands/labels.py` | `labels list/get/create/update/delete` |
| `src/readeck_cli/commands/collections.py` | `collections list/get/create/update/delete` |
| `src/readeck_cli/commands/highlights.py` | `highlights list/delete` |
| `src/readeck_cli/commands/profile.py` | `profile show` |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/unit/test_config.py` | Config loading logic |
| `tests/unit/test_output.py` | Output formatting |
| `tests/unit/test_models.py` | Pydantic model validation |
| `tests/integration/test_auth_service.py` | AuthService with respx mock |
| `tests/integration/test_bookmark_service.py` | BookmarkService with respx mock |
| `tests/integration/test_label_service.py` | LabelService with respx mock |
| `tests/integration/test_collection_service.py` | CollectionService with respx mock |
| `tests/integration/test_highlight_service.py` | HighlightService with respx mock |
| `tests/e2e/test_e2e.py` | End-to-end against real instance (skipped by default) |

---

## Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/readeck_cli/__init__.py`
- Create: `src/readeck_cli/client/__init__.py`
- Create: `src/readeck_cli/models/__init__.py`
- Create: `src/readeck_cli/services/__init__.py`
- Create: `src/readeck_cli/commands/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/e2e/__init__.py`

- [ ] **Step 1: Initialize uv project**

```bash
cd /path/to/readeck-claude-code
uv init --no-workspace --lib --python 3.13
```

Expected: creates `pyproject.toml`, `src/readeck_cli/__init__.py`, `uv.lock`.

- [ ] **Step 2: Replace pyproject.toml with full config**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "readeck-cli"
version = "0.1.0"
description = "CLI for Readeck read-it-later service"
requires-python = ">=3.13"
dependencies = [
    "typer>=0.12",
    "httpx>=0.27",
    "rich>=13",
    "pydantic>=2",
    "tomli-w>=1.0",
]

[project.scripts]
readeck-cli = "readeck_cli.main:app"

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "ruff>=0.4",
    "mypy>=1.10",
    "ty>=0.0.1a8",
    "pre-commit>=3",
]

[tool.hatch.build.targets.wheel]
packages = ["src/readeck_cli"]

[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "UP"]

[tool.mypy]
python_version = "3.13"
strict = true
explicit_package_bases = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
markers = [
    "e2e: end-to-end tests requiring a real Readeck instance",
]
testpaths = ["tests"]
```

- [ ] **Step 3: Install dependencies**

```bash
uv sync --group dev
```

Expected: creates `.venv/`, resolves all packages without errors.

- [ ] **Step 4: Create package structure**

```bash
mkdir -p src/readeck_cli/{client,models,services,commands}
mkdir -p tests/{unit,integration,e2e}
touch src/readeck_cli/{client,models,services,commands}/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/e2e/__init__.py
```

- [ ] **Step 5: Write .gitignore**

```gitignore
.claude/
.env
__pycache__/
*.pyc
*.pyo
.mypy_cache/
.ruff_cache/
.venv/
dist/
*.egg-info/
.pytest_cache/
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock .gitignore src/ tests/
git commit -m "feat: scaffold readeck-cli project with uv"
```

---

## Task 2: Pre-commit and GitHub Actions CI

**Files:**
- Create: `.pre-commit-config.yaml`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write .pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.1
    hooks:
      - id: mypy
        args: [src/]
        additional_dependencies:
          - pydantic
          - types-toml
          - httpx
          - typer
          - rich
  - repo: local
    hooks:
      - id: ty
        name: ty type check
        entry: uv run ty check src/
        language: system
        pass_filenames: false
        types: [python]
```

- [ ] **Step 2: Write .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - name: Install dependencies
        run: uv sync --group dev
      - name: ruff check
        run: uv run ruff check src/ tests/
      - name: ruff format check
        run: uv run ruff format --check src/ tests/
      - name: mypy
        run: uv run mypy src/
      - name: ty
        run: uv run ty check src/

  test:
    name: Test (Python 3.13)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - name: Install dependencies
        run: uv sync --group dev
      - name: Run unit + integration tests
        run: uv run pytest tests/unit tests/integration -v --tb=short
```

- [ ] **Step 3: Install pre-commit hooks**

```bash
uv run pre-commit install
```

Expected: `.git/hooks/pre-commit` created.

- [ ] **Step 4: Commit**

```bash
git add .pre-commit-config.yaml .github/
git commit -m "ci: add pre-commit hooks and GitHub Actions workflow"
```

---

## Task 3: Config module

**Files:**
- Create: `src/readeck_cli/config.py`
- Create: `tests/unit/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_config.py
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import tomllib
import tomli_w

from readeck_cli.config import Config, load_config, save_config, remove_token


def test_load_config_from_env(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"READECK_URL": "https://test.example.com", "READECK_TOKEN": "tok123"}):
        with patch("readeck_cli.config.CONFIG_FILE", tmp_path / "config.toml"):
            config = load_config()
    assert config.url == "https://test.example.com"
    assert config.token == "tok123"


def test_load_config_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(tomli_w.dumps({"default": {"url": "https://file.example.com", "token": "filetoken"}}))
    with patch.dict(os.environ, {}, clear=True):
        with patch("readeck_cli.config.CONFIG_FILE", config_file):
            config = load_config()
    assert config.url == "https://file.example.com"
    assert config.token == "filetoken"


def test_env_takes_precedence_over_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(tomli_w.dumps({"default": {"url": "https://file.example.com", "token": "filetoken"}}))
    with patch.dict(os.environ, {"READECK_URL": "https://env.example.com", "READECK_TOKEN": "envtoken"}):
        with patch("readeck_cli.config.CONFIG_FILE", config_file):
            config = load_config()
    assert config.url == "https://env.example.com"
    assert config.token == "envtoken"


def test_cli_flags_take_precedence_over_env(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"READECK_URL": "https://env.example.com", "READECK_TOKEN": "envtoken"}):
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
    config_file.write_bytes(tomli_w.dumps({"default": {"url": "https://x.com", "token": "abc"}}))
    with patch("readeck_cli.config.CONFIG_FILE", config_file):
        remove_token()
    data = tomllib.loads(config_file.read_text())
    assert "token" not in data.get("default", {})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected: `ImportError` — `readeck_cli.config` does not exist yet.

- [ ] **Step 3: Implement config.py**

```python
# src/readeck_cli/config.py
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Optional

import tomli_w
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".config" / "readeck"
CONFIG_FILE = CONFIG_DIR / "config.toml"


class Config(BaseModel):
    url: str
    token: str


def load_config(
    url: Optional[str] = None,
    token: Optional[str] = None,
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
            "No Readeck URL configured. Set READECK_URL or run 'readeck-cli auth login'."
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


def _read_config_file() -> dict[str, object]:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/readeck_cli/config.py tests/unit/test_config.py
git commit -m "feat: add config module (file + env vars, priority chain)"
```

---

## Task 4: HTTP client

**Files:**
- Create: `src/readeck_cli/client/http.py`
- Create: `tests/unit/test_http_client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_http_client.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient, ReadeckAPIError


BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@respx.mock
@pytest.mark.asyncio
async def test_get_success(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[{"id": "1"}])
    )
    response = await client.get("/api/bookmarks")
    assert response.status_code == 200
    assert response.json() == [{"id": "1"}]


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_401(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(ReadeckAPIError) as exc_info:
        await client.get("/api/bookmarks")
    assert exc_info.value.status_code == 401
    assert "token" in str(exc_info.value).lower()


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_404(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/missing").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(ReadeckAPIError) as exc_info:
        await client.get("/api/bookmarks/missing")
    assert exc_info.value.status_code == 404


@respx.mock
@pytest.mark.asyncio
async def test_bearer_token_injected(client: ReadeckClient) -> None:
    route = respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(200, json={})
    )
    await client.get("/api/profile")
    assert route.calls[0].request.headers["authorization"] == "Bearer testtoken"


@respx.mock
@pytest.mark.asyncio
async def test_post_success(client: ReadeckClient) -> None:
    respx.post(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(201, json={"id": "new"})
    )
    response = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    assert response.json()["id"] == "new"


@respx.mock
@pytest.mark.asyncio
async def test_delete_success(client: ReadeckClient) -> None:
    respx.delete(f"{BASE_URL}/api/bookmarks/1").mock(
        return_value=httpx.Response(204)
    )
    response = await client.delete("/api/bookmarks/1")
    assert response.status_code == 204


@respx.mock
@pytest.mark.asyncio
async def test_create_token_classmethod() -> None:
    respx.post(f"{BASE_URL}/api/auth").mock(
        return_value=httpx.Response(200, json={"id": "tid", "token": "newtoken"})
    )
    result = await ReadeckClient.create_token(BASE_URL, "user", "pass")
    assert result["token"] == "newtoken"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/test_http_client.py -v
```

Expected: `ImportError` — module does not exist yet.

- [ ] **Step 3: Implement client/http.py**

```python
# src/readeck_cli/client/http.py
from __future__ import annotations

from typing import Any

import httpx


class ReadeckAPIError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class ReadeckClient:
    def __init__(self, url: str, token: str) -> None:
        self._base_url = url.rstrip("/")
        self._token = token
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        response = await self._client.get(path, params=params)
        self._raise_for_status(response)
        return response

    async def post(self, path: str, json: dict[str, Any] | None = None) -> httpx.Response:
        response = await self._client.post(path, json=json)
        self._raise_for_status(response)
        return response

    async def patch(self, path: str, json: dict[str, Any] | None = None) -> httpx.Response:
        response = await self._client.patch(path, json=json)
        self._raise_for_status(response)
        return response

    async def delete(self, path: str) -> httpx.Response:
        response = await self._client.delete(path)
        self._raise_for_status(response)
        return response

    async def get_bytes(self, path: str) -> bytes:
        response = await self._client.get(path)
        self._raise_for_status(response)
        return response.content

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> ReadeckClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    @classmethod
    async def create_token(
        cls, url: str, username: str, password: str, application: str = "readeck-cli"
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=url.rstrip("/"), timeout=30.0) as client:
            response = await client.post(
                "/api/auth",
                json={"application": application, "username": username, "password": password},
            )
            if response.status_code == 401:
                raise ReadeckAPIError(401, "Invalid username or password.")
            if response.status_code >= 400:
                raise ReadeckAPIError(response.status_code, response.text)
            return dict(response.json())

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise ReadeckAPIError(401, "Invalid or expired token. Run 'readeck-cli auth login'.")
        if response.status_code == 403:
            raise ReadeckAPIError(403, "Forbidden.")
        if response.status_code == 404:
            raise ReadeckAPIError(404, "Resource not found.")
        if response.status_code == 422:
            raise ReadeckAPIError(422, f"Validation error: {response.text}")
        if response.status_code >= 500:
            raise ReadeckAPIError(response.status_code, f"Server error: {response.text}")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
uv run pytest tests/unit/test_http_client.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/readeck_cli/client/http.py tests/unit/test_http_client.py
git commit -m "feat: add ReadeckClient with HTTPX async and error handling"
```

---

## Task 5: Pydantic models

**Files:**
- Create: `src/readeck_cli/models/auth.py`
- Create: `src/readeck_cli/models/bookmark.py`
- Create: `src/readeck_cli/models/label.py`
- Create: `src/readeck_cli/models/collection.py`
- Create: `src/readeck_cli/models/highlight.py`
- Create: `src/readeck_cli/models/profile.py`
- Create: `tests/unit/test_models.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_models.py
from datetime import datetime

from readeck_cli.models.auth import TokenInfo
from readeck_cli.models.bookmark import Bookmark
from readeck_cli.models.label import Label
from readeck_cli.models.collection import Collection
from readeck_cli.models.highlight import Highlight
from readeck_cli.models.profile import UserProfile


def test_token_info_parses() -> None:
    data = {"id": "t1", "token": "abc123", "application": "readeck-cli", "created": "2026-01-01T00:00:00Z"}
    token = TokenInfo.model_validate(data)
    assert token.id == "t1"
    assert token.token == "abc123"


def test_bookmark_parses_minimal() -> None:
    data = {
        "id": "b1",
        "href": "/api/bookmarks/b1",
        "url": "https://example.com",
        "title": "Example",
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z",
    }
    bm = Bookmark.model_validate(data)
    assert bm.id == "b1"
    assert bm.url == "https://example.com"
    assert bm.labels == []
    assert bm.is_archived is False


def test_bookmark_parses_full() -> None:
    data = {
        "id": "b2",
        "href": "/api/bookmarks/b2",
        "url": "https://blog.example.com/post",
        "title": "A Post",
        "type": "article",
        "description": "Nice post",
        "authors": ["Alice"],
        "lang": "en",
        "labels": ["tech", "python"],
        "is_archived": True,
        "is_marked": False,
        "reading_time": 5,
        "word_count": 1200,
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-02T00:00:00Z",
        "site_name": "Example Blog",
    }
    bm = Bookmark.model_validate(data)
    assert bm.labels == ["tech", "python"]
    assert bm.is_archived is True
    assert bm.reading_time == 5


def test_label_parses() -> None:
    data = {"id": "l1", "label": "python", "count": 3}
    label = Label.model_validate(data)
    assert label.label == "python"
    assert label.count == 3


def test_collection_parses() -> None:
    data = {"id": "c1", "title": "Reading List", "created": "2026-01-01T00:00:00Z", "updated": "2026-01-01T00:00:00Z"}
    col = Collection.model_validate(data)
    assert col.title == "Reading List"


def test_highlight_parses() -> None:
    data = {"id": "h1", "bookmark_id": "b1", "text": "Important quote", "created": "2026-01-01T00:00:00Z"}
    h = Highlight.model_validate(data)
    assert h.text == "Important quote"


def test_user_profile_parses() -> None:
    data = {"id": "u1", "username": "stephane", "email": "stephane@example.com"}
    profile = UserProfile.model_validate(data)
    assert profile.username == "stephane"
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/unit/test_models.py -v
```

Expected: `ImportError` — models don't exist yet.

- [ ] **Step 3: Implement models**

```python
# src/readeck_cli/models/auth.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class TokenInfo(BaseModel):
    id: str
    token: str
    application: str
    created: datetime
    expires: datetime | None = None
```

```python
# src/readeck_cli/models/bookmark.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class BookmarkImage(BaseModel):
    src: str
    width: int | None = None
    height: int | None = None


class Bookmark(BaseModel):
    id: str
    href: str
    url: str
    title: str
    type: str | None = None
    description: str | None = None
    authors: list[str] = []
    lang: str | None = None
    labels: list[str] = []
    is_archived: bool = False
    is_marked: bool = False
    reading_time: int | None = None
    word_count: int | None = None
    created: datetime
    updated: datetime
    loaded: datetime | None = None
    site_name: str | None = None
    image: BookmarkImage | None = None
```

```python
# src/readeck_cli/models/label.py
from pydantic import BaseModel


class Label(BaseModel):
    id: str
    label: str
    count: int | None = None
```

```python
# src/readeck_cli/models/collection.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class Collection(BaseModel):
    id: str
    title: str
    created: datetime
    updated: datetime
```

```python
# src/readeck_cli/models/highlight.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class Highlight(BaseModel):
    id: str
    bookmark_id: str | None = None
    text: str
    created: datetime
    updated: datetime | None = None
```

```python
# src/readeck_cli/models/profile.py
from __future__ import annotations
from pydantic import BaseModel


class UserProfile(BaseModel):
    id: str | None = None
    username: str
    email: str | None = None
```

- [ ] **Step 4: Run to confirm pass**

```bash
uv run pytest tests/unit/test_models.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/readeck_cli/models/ tests/unit/test_models.py
git commit -m "feat: add Pydantic v2 models for all Readeck resources"
```

---

## Task 6: Output module

**Files:**
- Create: `src/readeck_cli/output.py`
- Create: `tests/unit/test_output.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_output.py
import json
from io import StringIO

from rich.console import Console

from readeck_cli.output import OutputFormat, render_table, render_json


def test_render_json_returns_valid_json(capsys: object) -> None:
    buf = StringIO()
    console = Console(file=buf, highlight=False)
    render_json([{"id": "1", "title": "Test"}], console=console)
    output = buf.getvalue()
    parsed = json.loads(output.strip())
    assert parsed[0]["id"] == "1"


def test_render_table_does_not_raise() -> None:
    buf = StringIO()
    console = Console(file=buf)
    render_table(
        headers=["ID", "Title"],
        rows=[["1", "Test Title"]],
        title="Bookmarks",
        console=console,
    )
    output = buf.getvalue()
    assert "Test Title" in output
    assert "Bookmarks" in output


def test_output_format_values() -> None:
    assert OutputFormat.TABLE == "table"
    assert OutputFormat.JSON == "json"
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/unit/test_output.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement output.py**

```python
# src/readeck_cli/output.py
from __future__ import annotations

import json
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table

_default_console = Console()


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"


def render_json(data: Any, console: Console | None = None) -> None:
    (console or _default_console).print(json.dumps(data, default=str, indent=2))


def render_table(
    headers: list[str],
    rows: list[list[str]],
    title: str | None = None,
    console: Console | None = None,
) -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    (console or _default_console).print(table)


def print_error(message: str, console: Console | None = None) -> None:
    (console or _default_console).print(f"[red]Error:[/red] {message}")


def print_success(message: str, console: Console | None = None) -> None:
    (console or _default_console).print(f"[green]✓[/green] {message}")
```

- [ ] **Step 4: Run to confirm pass**

```bash
uv run pytest tests/unit/test_output.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/readeck_cli/output.py tests/unit/test_output.py
git commit -m "feat: add output module (Rich table + JSON rendering)"
```

---

## Task 7: Auth service + command

**Files:**
- Create: `src/readeck_cli/services/auth.py`
- Create: `src/readeck_cli/commands/auth.py`
- Create: `tests/integration/test_auth_service.py`

- [ ] **Step 1: Write failing integration tests**

```python
# tests/integration/test_auth_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.auth import AuthService
from readeck_cli.models.auth import TokenInfo


BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> AuthService:
    return AuthService(client)


@respx.mock
@pytest.mark.asyncio
async def test_validate_token(service: AuthService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(200, json={"username": "stephane"})
    )
    result = await service.validate_token()
    assert result is True


@respx.mock
@pytest.mark.asyncio
async def test_validate_token_returns_false_on_401(service: AuthService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(401)
    )
    result = await service.validate_token()
    assert result is False
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_auth_service.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement services/auth.py**

```python
# src/readeck_cli/services/auth.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient


class AuthService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def validate_token(self) -> bool:
        try:
            await self._client.get("/api/profile")
            return True
        except ReadeckAPIError as e:
            if e.status_code == 401:
                return False
            raise
```

- [ ] **Step 4: Implement commands/auth.py**

```python
# src/readeck_cli/commands/auth.py
from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config, remove_token, save_config
from readeck_cli.models.auth import TokenInfo
from readeck_cli.output import print_error, print_success, render_table
from readeck_cli.services.auth import AuthService

app = typer.Typer(help="Authentication commands")


@app.command()
def login(
    url: Annotated[Optional[str], typer.Option(prompt=True, help="Readeck URL")] = None,
    username: Annotated[Optional[str], typer.Option(prompt=True, help="Username")] = None,
    password: Annotated[
        Optional[str], typer.Option(prompt=True, hide_input=True, help="Password")
    ] = None,
) -> None:
    """Login and save token to config."""
    assert url and username and password
    try:
        data = asyncio.run(ReadeckClient.create_token(url, username, password))
        token = TokenInfo.model_validate(data)
        save_config(url=url, token=token.token)
        print_success(f"Logged in as {username}. Token saved to config.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def logout() -> None:
    """Remove token from config."""
    remove_token()
    print_success("Token removed from config.")


@app.command()
def status(
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Show configured URL and validate token."""
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)

    async def _check() -> bool:
        async with ReadeckClient(config.url, config.token) as client:
            return await AuthService(client).validate_token()

    valid = asyncio.run(_check())
    render_table(
        headers=["URL", "Token", "Status"],
        rows=[[config.url, config.token[:8] + "…", "✓ valid" if valid else "✗ invalid"]],
        title="Auth Status",
    )


token_app = typer.Typer(help="Token management")
app.add_typer(token_app, name="token")


@token_app.command("set")
def token_set(
    value: Annotated[str, typer.Argument(help="API token")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL", help="Readeck URL")] = None,
) -> None:
    """Save a token manually without going through login."""
    try:
        config = load_config(url=url, token="placeholder")
        save_config(url=config.url, token=value)
    except ValueError:
        if not url:
            print_error("Provide --url or set READECK_URL.")
            raise typer.Exit(1)
        save_config(url=url, token=value)
    print_success("Token saved to config.")
```

- [ ] **Step 5: Run integration tests to confirm pass**

```bash
uv run pytest tests/integration/test_auth_service.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/auth.py src/readeck_cli/commands/auth.py tests/integration/test_auth_service.py
git commit -m "feat: add auth service and commands (login/logout/status/token set)"
```

---

## Task 8: Labels service + command

**Files:**
- Create: `src/readeck_cli/services/labels.py`
- Create: `src/readeck_cli/commands/labels.py`
- Create: `tests/integration/test_label_service.py`

- [ ] **Step 1: Write failing integration tests**

```python
# tests/integration/test_label_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.labels import LabelService
from readeck_cli.models.label import Label


BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> LabelService:
    return LabelService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_labels(service: LabelService) -> None:
    respx.get(f"{BASE_URL}/api/labels").mock(
        return_value=httpx.Response(200, json=[
            {"id": "l1", "label": "python", "count": 5},
            {"id": "l2", "label": "go", "count": 2},
        ])
    )
    labels = await service.list()
    assert len(labels) == 2
    assert labels[0].label == "python"


@respx.mock
@pytest.mark.asyncio
async def test_get_label(service: LabelService) -> None:
    respx.get(f"{BASE_URL}/api/labels/l1").mock(
        return_value=httpx.Response(200, json={"id": "l1", "label": "python", "count": 5})
    )
    label = await service.get("l1")
    assert label.id == "l1"


@respx.mock
@pytest.mark.asyncio
async def test_create_label(service: LabelService) -> None:
    respx.post(f"{BASE_URL}/api/labels").mock(
        return_value=httpx.Response(201, json={"id": "l3", "label": "rust", "count": 0})
    )
    label = await service.create("rust")
    assert label.label == "rust"


@respx.mock
@pytest.mark.asyncio
async def test_update_label(service: LabelService) -> None:
    respx.patch(f"{BASE_URL}/api/labels/l1").mock(
        return_value=httpx.Response(200, json={"id": "l1", "label": "python3", "count": 5})
    )
    label = await service.update("l1", name="python3")
    assert label.label == "python3"


@respx.mock
@pytest.mark.asyncio
async def test_delete_label(service: LabelService) -> None:
    respx.delete(f"{BASE_URL}/api/labels/l1").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("l1")
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_label_service.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement services/labels.py**

```python
# src/readeck_cli/services/labels.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.label import Label


class LabelService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self) -> list[Label]:
        response = await self._client.get("/api/labels")
        return [Label.model_validate(item) for item in response.json()]

    async def get(self, label_id: str) -> Label:
        response = await self._client.get(f"/api/labels/{label_id}")
        return Label.model_validate(response.json())

    async def create(self, name: str) -> Label:
        response = await self._client.post("/api/labels", json={"label": name})
        return Label.model_validate(response.json())

    async def update(self, label_id: str, name: str) -> Label:
        response = await self._client.patch(f"/api/labels/{label_id}", json={"label": name})
        return Label.model_validate(response.json())

    async def delete(self, label_id: str) -> None:
        await self._client.delete(f"/api/labels/{label_id}")
```

- [ ] **Step 4: Implement commands/labels.py**

```python
# src/readeck_cli/commands/labels.py
from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.output import OutputFormat, print_error, print_success, render_json, render_table
from readeck_cli.services.labels import LabelService

app = typer.Typer(help="Manage labels")


def _make_service(url: Optional[str], token: Optional[str]) -> tuple[ReadeckClient, LabelService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    client = ReadeckClient(config.url, config.token)
    return client, LabelService(client)


@app.command("list")
def list_labels(
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """List all labels."""
    client, service = _make_service(url, token)
    try:
        labels = asyncio.run(service.list())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json([{"id": l.id, "label": l.label, "count": l.count} for l in labels])
    else:
        render_table(
            headers=["ID", "Label", "Count"],
            rows=[[l.id, l.label, str(l.count or 0)] for l in labels],
            title=f"Labels ({len(labels)})",
        )


@app.command("get")
def get_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """Get a label by ID."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.get(label_id))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json({"id": label.id, "label": label.label, "count": label.count})
    else:
        render_table(headers=["ID", "Label", "Count"], rows=[[label.id, label.label, str(label.count or 0)]])


@app.command("create")
def create_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Create a new label."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.create(name))
        print_success(f"Label '{label.label}' created (id: {label.id})")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("update")
def update_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    name: Annotated[str, typer.Option("--name", help="New name")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Rename a label."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.update(label_id, name=name))
        print_success(f"Label updated to '{label.label}'")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("delete")
def delete_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    confirm: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
) -> None:
    """Delete a label."""
    if not confirm:
        typer.confirm(f"Delete label {label_id}?", abort=True)
    client, service = _make_service(url, token)
    try:
        asyncio.run(service.delete(label_id))
        print_success(f"Label {label_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())
```

- [ ] **Step 5: Run integration tests to confirm pass**

```bash
uv run pytest tests/integration/test_label_service.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/labels.py src/readeck_cli/commands/labels.py tests/integration/test_label_service.py
git commit -m "feat: add labels service and commands (CRUD)"
```

---

## Task 9: Bookmarks service + command

**Files:**
- Create: `src/readeck_cli/services/bookmarks.py`
- Create: `src/readeck_cli/commands/bookmarks.py`
- Create: `tests/integration/test_bookmark_service.py`

- [ ] **Step 1: Write failing integration tests**

```python
# tests/integration/test_bookmark_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.bookmarks import BookmarkService
from readeck_cli.models.bookmark import Bookmark

BASE_URL = "https://readeck.example.com"

BOOKMARK_DATA = {
    "id": "b1",
    "href": "/api/bookmarks/b1",
    "url": "https://example.com",
    "title": "Example",
    "labels": [],
    "is_archived": False,
    "is_marked": False,
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> BookmarkService:
    return BookmarkService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"})
    )
    bookmarks, total = await service.list()
    assert len(bookmarks) == 1
    assert total == 1
    assert bookmarks[0].url == "https://example.com"


@respx.mock
@pytest.mark.asyncio
async def test_get_bookmark(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(200, json=BOOKMARK_DATA)
    )
    bm = await service.get("b1")
    assert bm.id == "b1"


@respx.mock
@pytest.mark.asyncio
async def test_create_bookmark(service: BookmarkService) -> None:
    respx.post(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(201, json=BOOKMARK_DATA)
    )
    bm = await service.create("https://example.com")
    assert bm.url == "https://example.com"


@respx.mock
@pytest.mark.asyncio
async def test_update_bookmark(service: BookmarkService) -> None:
    updated = {**BOOKMARK_DATA, "title": "Updated Title"}
    respx.patch(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(200, json=updated)
    )
    bm = await service.update("b1", title="Updated Title")
    assert bm.title == "Updated Title"


@respx.mock
@pytest.mark.asyncio
async def test_delete_bookmark(service: BookmarkService) -> None:
    respx.delete(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("b1")


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"})
    )
    results = await service.search("example")
    assert len(results) == 1


@respx.mock
@pytest.mark.asyncio
async def test_fetch_all_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"})
    )
    bookmarks, _ = await service.list(fetch_all=True)
    assert len(bookmarks) == 1
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_bookmark_service.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement services/bookmarks.py**

```python
# src/readeck_cli/services/bookmarks.py
from __future__ import annotations

from typing import Any

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.bookmark import Bookmark


class BookmarkService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        fetch_all: bool = False,
    ) -> tuple[list[Bookmark], int]:
        if fetch_all:
            items = await self._fetch_all()
            return items, len(items)
        response = await self._client.get("/api/bookmarks", params={"page": page, "limit": limit})
        total = int(response.headers.get("X-Total-Count", 0))
        return [Bookmark.model_validate(item) for item in response.json()], total

    async def _fetch_all(self) -> list[Bookmark]:
        all_items: list[Bookmark] = []
        page = 1
        while True:
            response = await self._client.get("/api/bookmarks", params={"page": page, "limit": 100})
            total = int(response.headers.get("X-Total-Count", 0))
            items = response.json()
            if not items:
                break
            all_items.extend(Bookmark.model_validate(item) for item in items)
            if len(all_items) >= total:
                break
            page += 1
        return all_items

    async def get(self, bookmark_id: str) -> Bookmark:
        response = await self._client.get(f"/api/bookmarks/{bookmark_id}")
        return Bookmark.model_validate(response.json())

    async def create(self, url: str) -> Bookmark:
        response = await self._client.post("/api/bookmarks", json={"url": url})
        return Bookmark.model_validate(response.json())

    async def update(self, bookmark_id: str, **kwargs: Any) -> Bookmark:
        response = await self._client.patch(f"/api/bookmarks/{bookmark_id}", json=kwargs)
        return Bookmark.model_validate(response.json())

    async def delete(self, bookmark_id: str) -> None:
        await self._client.delete(f"/api/bookmarks/{bookmark_id}")

    async def search(self, query: str) -> list[Bookmark]:
        response = await self._client.get("/api/bookmarks", params={"search": query, "limit": 100})
        return [Bookmark.model_validate(item) for item in response.json()]

    async def export(self, bookmark_id: str, fmt: str = "epub") -> bytes:
        return await self._client.get_bytes(f"/api/bookmarks/{bookmark_id}/{fmt}")
```

- [ ] **Step 4: Implement commands/bookmarks.py**

```python
# src/readeck_cli/commands/bookmarks.py
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.output import OutputFormat, print_error, print_success, render_json, render_table
from readeck_cli.services.bookmarks import BookmarkService

app = typer.Typer(help="Manage bookmarks")


def _make_service(url: Optional[str], token: Optional[str]) -> tuple[ReadeckClient, BookmarkService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    client = ReadeckClient(config.url, config.token)
    return client, BookmarkService(client)


def _bookmark_row(bm: object) -> list[str]:
    from readeck_cli.models.bookmark import Bookmark
    assert isinstance(bm, Bookmark)
    return [
        bm.id,
        bm.title[:60] + ("…" if len(bm.title) > 60 else ""),
        bm.url[:50] + ("…" if len(bm.url) > 50 else ""),
        "✓" if bm.is_archived else "",
        str(bm.reading_time or ""),
        ",".join(bm.labels),
    ]


@app.command("list")
def list_bookmarks(
    page: Annotated[int, typer.Option("--page", "-p")] = 1,
    limit: Annotated[int, typer.Option("--limit", "-l")] = 20,
    all_pages: Annotated[bool, typer.Option("--all")] = False,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """List bookmarks."""
    client, service = _make_service(url, token)
    try:
        bookmarks, total = asyncio.run(service.list(page=page, limit=limit, fetch_all=all_pages))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json([bm.model_dump(mode="json") for bm in bookmarks])
    else:
        render_table(
            headers=["ID", "Title", "URL", "Archived", "Read (min)", "Labels"],
            rows=[_bookmark_row(bm) for bm in bookmarks],
            title=f"Bookmarks (page {page}, total {total})",
        )


@app.command("get")
def get_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """Get a bookmark by ID."""
    client, service = _make_service(url, token)
    try:
        bm = asyncio.run(service.get(bookmark_id))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json(bm.model_dump(mode="json"))
    else:
        render_table(
            headers=["Field", "Value"],
            rows=[
                ["ID", bm.id],
                ["Title", bm.title],
                ["URL", bm.url],
                ["Labels", ", ".join(bm.labels)],
                ["Archived", str(bm.is_archived)],
                ["Reading time", f"{bm.reading_time} min" if bm.reading_time else ""],
                ["Created", str(bm.created)],
            ],
        )


@app.command("add")
def add_bookmark(
    bookmark_url: Annotated[str, typer.Argument(metavar="URL")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Add a new bookmark."""
    client, service = _make_service(url, token)
    try:
        bm = asyncio.run(service.create(bookmark_url))
        print_success(f"Bookmark created: {bm.id} — {bm.title}")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("update")
def update_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    title: Annotated[Optional[str], typer.Option("--title")] = None,
    labels: Annotated[Optional[str], typer.Option("--labels", help="Comma-separated labels")] = None,
    is_archived: Annotated[Optional[bool], typer.Option("--archived/--no-archived")] = None,
    is_marked: Annotated[Optional[bool], typer.Option("--marked/--no-marked")] = None,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Update a bookmark."""
    updates: dict[str, object] = {}
    if title is not None:
        updates["title"] = title
    if labels is not None:
        updates["labels"] = [l.strip() for l in labels.split(",")]
    if is_archived is not None:
        updates["is_archived"] = is_archived
    if is_marked is not None:
        updates["is_marked"] = is_marked
    if not updates:
        print_error("No fields to update.")
        raise typer.Exit(1)

    client, service = _make_service(url, token)
    try:
        bm = asyncio.run(service.update(bookmark_id, **updates))
        print_success(f"Bookmark {bm.id} updated.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("delete")
def delete_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a bookmark."""
    if not confirm:
        typer.confirm(f"Delete bookmark {bookmark_id}?", abort=True)
    client, service = _make_service(url, token)
    try:
        asyncio.run(service.delete(bookmark_id))
        print_success(f"Bookmark {bookmark_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("search")
def search_bookmarks(
    query: Annotated[str, typer.Argument()],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """Full-text search bookmarks."""
    client, service = _make_service(url, token)
    try:
        bookmarks = asyncio.run(service.search(query))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json([bm.model_dump(mode="json") for bm in bookmarks])
    else:
        render_table(
            headers=["ID", "Title", "URL", "Archived", "Read (min)", "Labels"],
            rows=[_bookmark_row(bm) for bm in bookmarks],
            title=f"Search results for '{query}' ({len(bookmarks)})",
        )


@app.command("export")
def export_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    fmt: Annotated[str, typer.Option("--format", "-f", help="epub or pdf")] = "epub",
    dest: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Export a bookmark as epub or pdf."""
    client, service = _make_service(url, token)
    try:
        content = asyncio.run(service.export(bookmark_id, fmt=fmt))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    out_path = dest or Path(f"{bookmark_id}.{fmt}")
    out_path.write_bytes(content)
    print_success(f"Exported to {out_path}")
```

- [ ] **Step 5: Run integration tests to confirm pass**

```bash
uv run pytest tests/integration/test_bookmark_service.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/bookmarks.py src/readeck_cli/commands/bookmarks.py tests/integration/test_bookmark_service.py
git commit -m "feat: add bookmarks service and commands (list/get/add/update/delete/search/export)"
```

---

## Task 10: Collections service + command

**Files:**
- Create: `src/readeck_cli/services/collections.py`
- Create: `src/readeck_cli/commands/collections.py`
- Create: `tests/integration/test_collection_service.py`

- [ ] **Step 1: Write failing integration tests**

```python
# tests/integration/test_collection_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.collections import CollectionService

BASE_URL = "https://readeck.example.com"

COLLECTION_DATA = {
    "id": "c1",
    "title": "Reading List",
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> CollectionService:
    return CollectionService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_collections(service: CollectionService) -> None:
    respx.get(f"{BASE_URL}/api/collections").mock(
        return_value=httpx.Response(200, json=[COLLECTION_DATA])
    )
    collections = await service.list()
    assert len(collections) == 1
    assert collections[0].title == "Reading List"


@respx.mock
@pytest.mark.asyncio
async def test_get_collection(service: CollectionService) -> None:
    respx.get(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(200, json=COLLECTION_DATA)
    )
    col = await service.get("c1")
    assert col.id == "c1"


@respx.mock
@pytest.mark.asyncio
async def test_create_collection(service: CollectionService) -> None:
    respx.post(f"{BASE_URL}/api/collections").mock(
        return_value=httpx.Response(201, json=COLLECTION_DATA)
    )
    col = await service.create("Reading List")
    assert col.title == "Reading List"


@respx.mock
@pytest.mark.asyncio
async def test_update_collection(service: CollectionService) -> None:
    updated = {**COLLECTION_DATA, "title": "Archive"}
    respx.patch(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(200, json=updated)
    )
    col = await service.update("c1", title="Archive")
    assert col.title == "Archive"


@respx.mock
@pytest.mark.asyncio
async def test_delete_collection(service: CollectionService) -> None:
    respx.delete(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("c1")
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_collection_service.py -v
```

- [ ] **Step 3: Implement services/collections.py**

```python
# src/readeck_cli/services/collections.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.collection import Collection


class CollectionService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self) -> list[Collection]:
        response = await self._client.get("/api/collections")
        return [Collection.model_validate(item) for item in response.json()]

    async def get(self, collection_id: str) -> Collection:
        response = await self._client.get(f"/api/collections/{collection_id}")
        return Collection.model_validate(response.json())

    async def create(self, title: str) -> Collection:
        response = await self._client.post("/api/collections", json={"title": title})
        return Collection.model_validate(response.json())

    async def update(self, collection_id: str, title: str) -> Collection:
        response = await self._client.patch(f"/api/collections/{collection_id}", json={"title": title})
        return Collection.model_validate(response.json())

    async def delete(self, collection_id: str) -> None:
        await self._client.delete(f"/api/collections/{collection_id}")
```

- [ ] **Step 4: Implement commands/collections.py**

```python
# src/readeck_cli/commands/collections.py
from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.output import OutputFormat, print_error, print_success, render_json, render_table
from readeck_cli.services.collections import CollectionService

app = typer.Typer(help="Manage collections")


def _make_service(url: Optional[str], token: Optional[str]) -> tuple[ReadeckClient, CollectionService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    client = ReadeckClient(config.url, config.token)
    return client, CollectionService(client)


@app.command("list")
def list_collections(
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """List all collections."""
    client, service = _make_service(url, token)
    try:
        collections = asyncio.run(service.list())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json([col.model_dump(mode="json") for col in collections])
    else:
        render_table(
            headers=["ID", "Title", "Created"],
            rows=[[col.id, col.title, str(col.created.date())] for col in collections],
            title=f"Collections ({len(collections)})",
        )


@app.command("get")
def get_collection(
    collection_id: Annotated[str, typer.Argument()],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """Get a collection by ID."""
    client, service = _make_service(url, token)
    try:
        col = asyncio.run(service.get(collection_id))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json(col.model_dump(mode="json"))
    else:
        render_table(headers=["Field", "Value"], rows=[["ID", col.id], ["Title", col.title], ["Created", str(col.created)]])


@app.command("create")
def create_collection(
    title: Annotated[str, typer.Argument()],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Create a new collection."""
    client, service = _make_service(url, token)
    try:
        col = asyncio.run(service.create(title))
        print_success(f"Collection '{col.title}' created (id: {col.id})")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("update")
def update_collection(
    collection_id: Annotated[str, typer.Argument()],
    title: Annotated[str, typer.Option("--title")],
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Rename a collection."""
    client, service = _make_service(url, token)
    try:
        col = asyncio.run(service.update(collection_id, title=title))
        print_success(f"Collection updated to '{col.title}'")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())


@app.command("delete")
def delete_collection(
    collection_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a collection."""
    if not confirm:
        typer.confirm(f"Delete collection {collection_id}?", abort=True)
    client, service = _make_service(url, token)
    try:
        asyncio.run(service.delete(collection_id))
        print_success(f"Collection {collection_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())
```

- [ ] **Step 5: Run to confirm pass**

```bash
uv run pytest tests/integration/test_collection_service.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/collections.py src/readeck_cli/commands/collections.py tests/integration/test_collection_service.py
git commit -m "feat: add collections service and commands (CRUD)"
```

---

## Task 11: Highlights service + command

**Files:**
- Create: `src/readeck_cli/services/highlights.py`
- Create: `src/readeck_cli/commands/highlights.py`
- Create: `tests/integration/test_highlight_service.py`

- [ ] **Step 1: Write failing integration tests**

```python
# tests/integration/test_highlight_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.highlights import HighlightService

BASE_URL = "https://readeck.example.com"

HIGHLIGHT_DATA = {
    "id": "h1",
    "bookmark_id": "b1",
    "text": "Important quote",
    "created": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> HighlightService:
    return HighlightService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_highlights(service: HighlightService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/b1/highlights").mock(
        return_value=httpx.Response(200, json=[HIGHLIGHT_DATA])
    )
    highlights = await service.list(bookmark_id="b1")
    assert len(highlights) == 1
    assert highlights[0].text == "Important quote"


@respx.mock
@pytest.mark.asyncio
async def test_list_all_highlights(service: HighlightService) -> None:
    respx.get(f"{BASE_URL}/api/highlights").mock(
        return_value=httpx.Response(200, json=[HIGHLIGHT_DATA])
    )
    highlights = await service.list()
    assert len(highlights) == 1


@respx.mock
@pytest.mark.asyncio
async def test_delete_highlight(service: HighlightService) -> None:
    respx.delete(f"{BASE_URL}/api/highlights/h1").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("h1")
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_highlight_service.py -v
```

- [ ] **Step 3: Implement services/highlights.py**

```python
# src/readeck_cli/services/highlights.py
from __future__ import annotations

from typing import Optional

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.highlight import Highlight


class HighlightService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self, bookmark_id: Optional[str] = None) -> list[Highlight]:
        if bookmark_id:
            path = f"/api/bookmarks/{bookmark_id}/highlights"
        else:
            path = "/api/highlights"
        response = await self._client.get(path)
        return [Highlight.model_validate(item) for item in response.json()]

    async def delete(self, highlight_id: str) -> None:
        await self._client.delete(f"/api/highlights/{highlight_id}")
```

- [ ] **Step 4: Implement commands/highlights.py**

```python
# src/readeck_cli/commands/highlights.py
from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.output import OutputFormat, print_error, print_success, render_json, render_table
from readeck_cli.services.highlights import HighlightService

app = typer.Typer(help="Manage highlights")


def _make_service(url: Optional[str], token: Optional[str]) -> tuple[ReadeckClient, HighlightService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    client = ReadeckClient(config.url, config.token)
    return client, HighlightService(client)


@app.command("list")
def list_highlights(
    bookmark: Annotated[Optional[str], typer.Option("--bookmark", "-b", help="Filter by bookmark ID")] = None,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """List highlights (optionally filtered by bookmark)."""
    client, service = _make_service(url, token)
    try:
        highlights = asyncio.run(service.list(bookmark_id=bookmark))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json([h.model_dump(mode="json") for h in highlights])
    else:
        render_table(
            headers=["ID", "Bookmark", "Text", "Created"],
            rows=[[h.id, h.bookmark_id or "", h.text[:80] + ("…" if len(h.text) > 80 else ""), str(h.created.date())] for h in highlights],
            title=f"Highlights ({len(highlights)})",
        )


@app.command("delete")
def delete_highlight(
    highlight_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a highlight."""
    if not confirm:
        typer.confirm(f"Delete highlight {highlight_id}?", abort=True)
    client, service = _make_service(url, token)
    try:
        asyncio.run(service.delete(highlight_id))
        print_success(f"Highlight {highlight_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)
    finally:
        asyncio.run(client.aclose())
```

- [ ] **Step 5: Run to confirm pass**

```bash
uv run pytest tests/integration/test_highlight_service.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/highlights.py src/readeck_cli/commands/highlights.py tests/integration/test_highlight_service.py
git commit -m "feat: add highlights service and commands (list/delete)"
```

---

## Task 12: Profile service + command

**Files:**
- Create: `src/readeck_cli/services/profile.py`
- Create: `src/readeck_cli/commands/profile.py`

- [ ] **Step 1: Write failing integration test**

```python
# tests/integration/test_profile_service.py
import pytest
import respx
import httpx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.profile import ProfileService

BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> ProfileService:
    return ProfileService(client)


@respx.mock
@pytest.mark.asyncio
async def test_get_profile(service: ProfileService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(200, json={"username": "stephane", "email": "s@example.com"})
    )
    profile = await service.get()
    assert profile.username == "stephane"
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/integration/test_profile_service.py -v
```

- [ ] **Step 3: Implement services/profile.py**

```python
# src/readeck_cli/services/profile.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.profile import UserProfile


class ProfileService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def get(self) -> UserProfile:
        response = await self._client.get("/api/profile")
        return UserProfile.model_validate(response.json())
```

- [ ] **Step 4: Implement commands/profile.py**

```python
# src/readeck_cli/commands/profile.py
from __future__ import annotations

import asyncio
from typing import Annotated, Optional

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.output import OutputFormat, print_error, render_json, render_table
from readeck_cli.services.profile import ProfileService

app = typer.Typer(help="User profile")


@app.command("show")
def show_profile(
    url: Annotated[Optional[str], typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[Optional[str], typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.TABLE,
) -> None:
    """Show current user profile."""
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)

    async def _get() -> object:
        async with ReadeckClient(config.url, config.token) as client:
            return await ProfileService(client).get()

    try:
        profile = asyncio.run(_get())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1)

    from readeck_cli.models.profile import UserProfile
    assert isinstance(profile, UserProfile)

    if output == OutputFormat.JSON:
        render_json(profile.model_dump(mode="json"))
    else:
        render_table(
            headers=["Field", "Value"],
            rows=[
                ["Username", profile.username],
                ["Email", profile.email or ""],
            ],
            title="Profile",
        )
```

- [ ] **Step 5: Run to confirm pass**

```bash
uv run pytest tests/integration/test_profile_service.py -v
```

Expected: 1 test PASS.

- [ ] **Step 6: Commit**

```bash
git add src/readeck_cli/services/profile.py src/readeck_cli/commands/profile.py tests/integration/test_profile_service.py
git commit -m "feat: add profile service and command"
```

---

## Task 13: Main entry point

**Files:**
- Create: `src/readeck_cli/main.py`
- Create: `tests/unit/test_main.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_main.py
from typer.testing import CliRunner
from readeck_cli.main import app

runner = CliRunner()


def test_app_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "readeck-cli" in result.output.lower() or "usage" in result.output.lower()


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
```

- [ ] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/unit/test_main.py -v
```

Expected: `ImportError` — `main.py` does not exist.

- [ ] **Step 3: Implement main.py**

```python
# src/readeck_cli/main.py
from __future__ import annotations

import typer

from readeck_cli.commands import auth, bookmarks, collections, highlights, labels, profile

app = typer.Typer(
    name="readeck-cli",
    help="CLI for Readeck read-it-later service.",
    no_args_is_help=True,
)

app.add_typer(auth.app, name="auth")
app.add_typer(bookmarks.app, name="bookmarks")
app.add_typer(labels.app, name="labels")
app.add_typer(collections.app, name="collections")
app.add_typer(highlights.app, name="highlights")
app.add_typer(profile.app, name="profile")

if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run to confirm pass**

```bash
uv run pytest tests/unit/test_main.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 5: Run the full test suite**

```bash
uv run pytest tests/unit tests/integration -v
```

Expected: all tests PASS, 0 errors.

- [ ] **Step 6: Run linters**

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
```

Expected: no errors (fix any that appear before committing).

- [ ] **Step 7: Commit**

```bash
git add src/readeck_cli/main.py tests/unit/test_main.py
git commit -m "feat: wire all commands into main Typer app"
```

---

## Task 14: E2E test setup

**Files:**
- Create: `tests/e2e/test_e2e.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py with shared fixtures**

```python
# tests/conftest.py
import os
import pytest
from readeck_cli.client.http import ReadeckClient
from readeck_cli.config import Config


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring READECK_URL + READECK_TOKEN")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("READECK_E2E") != "1":
        skip = pytest.mark.skip(reason="Set READECK_E2E=1 to run e2e tests")
        for item in items:
            if item.get_closest_marker("e2e"):
                item.add_marker(skip)


@pytest.fixture
def e2e_config() -> Config:
    url = os.environ.get("READECK_URL")
    token = os.environ.get("READECK_TOKEN")
    if not url or not token:
        pytest.skip("READECK_URL and READECK_TOKEN required")
    return Config(url=url, token=token)


@pytest.fixture
async def e2e_client(e2e_config: Config) -> ReadeckClient:
    async with ReadeckClient(e2e_config.url, e2e_config.token) as client:
        yield client
```

- [ ] **Step 2: Write e2e tests**

```python
# tests/e2e/test_e2e.py
import pytest
from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.bookmarks import BookmarkService
from readeck_cli.services.labels import LabelService
from readeck_cli.services.profile import ProfileService


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_profile_returns_username(e2e_client: ReadeckClient) -> None:
    service = ProfileService(e2e_client)
    profile = await service.get()
    assert profile.username


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_list_bookmarks_returns_list(e2e_client: ReadeckClient) -> None:
    service = BookmarkService(e2e_client)
    bookmarks, total = await service.list(limit=5)
    assert isinstance(bookmarks, list)
    assert total >= 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_list_labels_returns_list(e2e_client: ReadeckClient) -> None:
    service = LabelService(e2e_client)
    labels = await service.list()
    assert isinstance(labels, list)
```

- [ ] **Step 3: Confirm e2e tests are skipped by default**

```bash
uv run pytest tests/e2e/ -v
```

Expected: all tests SKIPPED with message "Set READECK_E2E=1 to run e2e tests".

- [ ] **Step 4: Run full suite one last time**

```bash
uv run pytest tests/unit tests/integration -v --tb=short
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/conftest.py tests/e2e/test_e2e.py
git commit -m "test: add E2E test setup (skipped by default, READECK_E2E=1 to enable)"
```

---

## Notes on API endpoint compatibility

The models and service endpoints in this plan are based on the Readeck open-source codebase conventions. If the actual API at your instance uses slightly different field names or response structures, adjust the Pydantic models in `src/readeck_cli/models/` — the services and commands will automatically benefit. Running `readeck-cli auth status` against your instance is a good first smoke test.

To inspect the actual API schema, visit `https://readeck.mgx.io/api/swagger` (if Swagger UI is enabled) or `GET /api/` for the OpenAPI spec.
