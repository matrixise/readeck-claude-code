# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (including dev)
uv sync --group dev

# Run all unit + integration tests
uv run pytest tests/unit tests/integration -v

# Run a single test file
uv run pytest tests/unit/test_config.py -v

# Run a single test by name
uv run pytest tests/integration/test_bookmark_service.py::test_list_bookmarks -v

# Run E2E tests (requires a live Readeck instance)
READECK_E2E=1 READECK_URL=https://... READECK_TOKEN=... uv run pytest tests/e2e -v

# Lint
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
uv run ty check src/

# Run pre-commit hooks on all files
prek run --all-files
```

## Architecture

Data flows top-down through three layers:

```
Typer command → Service → ReadeckClient (HTTPX async) → Pydantic model → output.py → terminal
```

**`client/http.py`** — `ReadeckClient` wraps HTTPX async, injects Bearer token, maps HTTP errors (401/403/404/422/5xx) to `ReadeckAPIError`. Use as async context manager or call `aclose()` explicitly. `create_token()` is a classmethod for the login flow (no auth required).

**`services/`** — One class per resource (`BookmarkService`, `LabelService`, etc.). All methods are `async`. Services receive a `ReadeckClient` instance and return typed Pydantic models. Pagination in `BookmarkService.list()` uses the `X-Total-Count` response header; `--all` triggers `_fetch_all()` which pages at 100 items. `BookmarkService.search()` accepts all `GET /api/bookmarks` query parameters (search, title, author, site, type, labels, range_start, range_end, read_status, is_archived, is_marked, has_labels, has_errors, is_loaded, id, collection, sort, limit) and passes them through as query params.

**`commands/`** — Thin Typer wrappers. Each command calls `_make_service(url, token)` to load config, instantiates the client, calls `asyncio.run()` on the service method, then closes the client in a `finally` block. Every command accepts `--url` / `--token` flags (also read from `READECK_URL` / `READECK_TOKEN` env vars) and most accept `--output [table|json]`.

**`config.py`** — `load_config()` resolves credentials with priority: CLI flags → `READECK_URL`/`READECK_TOKEN` env vars → `~/.config/readeck/config.toml` `[default]` section. Raises `ValueError` if URL or token is missing. `CONFIG_DIR` and `CONFIG_FILE` are module-level `Path` constants — patch them in tests to avoid touching the real filesystem.

**`output.py`** — `render_table()` and `render_json()` accept an optional `console` argument for testing. `OutputFormat` is a `StrEnum` with `TABLE` and `JSON`.

**`models/`** — Pydantic v2 models matching Readeck API response schemas. All fields are validated with `model_validate()`.

## Testing patterns

Integration tests use `respx` to mock HTTPX at the transport level — no real HTTP requests. Tests are `async` with `@pytest.mark.asyncio` (mode is `auto` in `pyproject.toml`). E2E tests are marked `@pytest.mark.e2e` and skipped unless `READECK_E2E=1` is set.

## Tooling notes

- **prek** (Rust-based hook runner) uses `prek.toml`. Hooks: `ruff` (lint+fix), `ruff-format`, `mypy`, `ty`. The warning about multiple config files (`prek.toml` + `.pre-commit-config.yaml`) is benign — prek uses `prek.toml`.
- **ruff isort**: `readeck_cli` is declared as `known-first-party` in `pyproject.toml` — required for consistent import ordering between prek's ruff and CI's ruff.
- Source layout: package is under `src/readeck_cli/`, which requires `mypy_path = "src"` and `explicit_package_bases = true` in `pyproject.toml`.
