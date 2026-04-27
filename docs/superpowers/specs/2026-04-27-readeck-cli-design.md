# Readeck CLI — Design Spec

**Date:** 2026-04-27  
**Project:** `readeck-cli`  
**Author:** Stéphane Wirtel

---

## Overview

A CLI application to interact with a self-hosted Readeck instance via its REST API. Built with Typer, HTTPX (async), Pydantic, and Rich. Installable as a standalone tool via `uv tool install`.

---

## Decisions Summary

| Topic | Decision |
|---|---|
| Config | File `~/.config/readeck/config.toml` + env vars (env vars take precedence) |
| Scope | Full API coverage: bookmarks, labels, collections, highlights, profile |
| Output | Rich table by default, `--output json` flag |
| Auth | `auth login` interactive + manual token in config |
| Pagination | `--page`/`--limit` by default, `--all` to fetch everything |
| Binary name | `readeck-cli` |
| Tests | Unit + integration (respx mock) + optional E2E |
| Python | 3.13+ |
| Structure | 3-layer: client / services / commands |
| Distribution | Entry point in `pyproject.toml`, PyPI later |

---

## Project Structure

```
readeck-claude-code/
├── src/
│   └── readeck_cli/
│       ├── __init__.py
│       ├── main.py              # Entry point Typer app
│       ├── config.py            # Config file + env vars resolution
│       ├── output.py            # Table (rich) / JSON formatting
│       ├── client/
│       │   ├── __init__.py
│       │   └── http.py          # ReadeckClient (HTTPX async, auth, error handling)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── bookmark.py
│       │   ├── label.py
│       │   ├── collection.py
│       │   └── highlight.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── bookmarks.py
│       │   ├── labels.py
│       │   ├── collections.py
│       │   └── highlights.py
│       └── commands/
│           ├── __init__.py
│           ├── auth.py
│           ├── bookmarks.py
│           ├── labels.py
│           ├── collections.py
│           └── highlights.py
├── tests/
│   ├── unit/
│   ├── integration/             # respx (HTTPX mock)
│   └── e2e/                     # Requires READECK_URL + READECK_TOKEN, skipped by default
├── docs/
│   └── superpowers/
│       └── specs/
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── .pre-commit-config.yaml
├── .gitignore
└── .claude/                     # Git worktrees (gitignored)
```

---

## Architecture

**Data flow:**
```
Typer Command → Service → ReadeckClient (HTTPX) → Pydantic Model → output.py → terminal
```

Each layer has a single responsibility:
- **`client/http.py`** — raw HTTP: injects Bearer token, handles HTTP errors (401, 404, 5xx) with clear messages
- **`services/`** — business logic per resource, pagination handling, returns typed Pydantic models
- **`commands/`** — thin Typer wrappers that call services via `asyncio.run()`, then pass results to `output.py`
- **`models/`** — Pydantic v2 models matching Readeck API response schemas
- **`output.py`** — renders Rich tables or JSON depending on `--output` flag

---

## Configuration

**File:** `~/.config/readeck/config.toml`

```toml
[default]
url = "https://readeck.mgx.io"
token = "your-api-token"
```

**Resolution priority (highest to lowest):**
1. `--url` / `--token` flags (per-command override)
2. `READECK_URL` / `READECK_TOKEN` environment variables
3. `~/.config/readeck/config.toml` `[default]` section
4. Explicit error if nothing is configured

---

## Authentication Commands

```
readeck-cli auth login          # Prompts URL + username + password → creates token via API → saves to config
readeck-cli auth logout         # Removes token from config file
readeck-cli auth status         # Shows configured URL, validates token against API
readeck-cli auth token set      # Saves a token manually (no login flow)
```

---

## Commands

### Bookmarks
```
readeck-cli bookmarks list              # Paginated list (--page, --limit, --all)
readeck-cli bookmarks get <id>          # Bookmark detail
readeck-cli bookmarks add <url>         # Create bookmark
readeck-cli bookmarks update <id>       # Edit (--title, --labels, --is-read, etc.)
readeck-cli bookmarks delete <id>       # Delete
readeck-cli bookmarks search <query>    # Full-text search
readeck-cli bookmarks export <id>       # Export (--format epub|pdf)
```

### Labels
```
readeck-cli labels list
readeck-cli labels get <id-or-slug>
readeck-cli labels create <name>
readeck-cli labels update <id> --name <new-name>
readeck-cli labels delete <id>
```

### Collections
```
readeck-cli collections list
readeck-cli collections get <id>
readeck-cli collections create <name>
readeck-cli collections update <id>
readeck-cli collections delete <id>
```

### Highlights
```
readeck-cli highlights list                         # All highlights
readeck-cli highlights list --bookmark <id>         # Highlights for a bookmark
readeck-cli highlights delete <id>
```

### Profile
```
readeck-cli profile show                            # Current user info
```

### Global flags (all commands)
- `--output [table|json]` — output format
- `--url <url>` — override configured URL
- `--token <token>` — override configured token

---

## Dependencies

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "typer",
    "httpx",
    "rich",
    "pydantic>=2",
    "tomli-w",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
    "respx",
    "ruff",
    "mypy",
    "ty",
    "pre-commit",
]
```

---

## Tooling

### Pre-commit hooks
- `ruff check --fix` — linting with auto-fix
- `ruff format` — formatting (replaces black)
- `mypy` — strict type checking
- `ty check` — fast type checking (Astral)

### GitHub Actions CI (`.github/workflows/ci.yml`)
- Triggers: push and PR to `main`
- Jobs:
  - `lint`: `ruff check`, `ruff format --check`, `mypy`, `ty check`
  - `test`: `pytest tests/unit tests/integration`
- Matrix: Python 3.13
- `uv` cache for fast installs

### Git worktrees
- Stored in `.claude/worktrees/` (gitignored)

---

## Testing Strategy

| Layer | Tool | Location |
|---|---|---|
| Unit | pytest | `tests/unit/` |
| Integration | pytest + respx | `tests/integration/` |
| E2E | pytest + real instance | `tests/e2e/` (skipped by default, requires env vars) |

E2E tests are marked `@pytest.mark.e2e` and skipped unless `READECK_E2E=1` is set.

---

## `.gitignore` entries

```
.cloud/
.env
__pycache__/
*.pyc
.mypy_cache/
.ruff_cache/
dist/
```
