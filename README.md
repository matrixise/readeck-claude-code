# readeck-cli

A command-line interface for [Readeck](https://readeck.org), a self-hosted read-it-later service. Built with Python 3.13, Typer, HTTPX (async), Pydantic, and Rich.

## Installation

```bash
uv tool install readeck-cli
```

Or install from source:

```bash
git clone https://github.com/matrixise/readeck-cli
cd readeck-cli
uv sync
```

## Configuration

Credentials are resolved in this order:

1. `--url` / `--token` flags on the command
2. `READECK_URL` / `READECK_TOKEN` environment variables
3. `~/.config/readeck/config.toml`

### Login

```bash
readeck-cli auth login
# prompts for URL, username, password → saves token to ~/.config/readeck/config.toml
```

### Manual token

```bash
readeck-cli auth token set <token> --url https://readeck.example.com
```

### Check status

```bash
readeck-cli auth status
```

## Commands

### Bookmarks

```bash
readeck-cli bookmarks list                        # paginated (--page, --limit)
readeck-cli bookmarks list --all                  # fetch everything
readeck-cli bookmarks get <id>
readeck-cli bookmarks add <url>
readeck-cli bookmarks update <id> --title "New title" --labels "work,python"
readeck-cli bookmarks update <id> --archived
readeck-cli bookmarks delete <id>
readeck-cli bookmarks search --search <query>
readeck-cli bookmarks search --title "python" --sort -created
readeck-cli bookmarks search --range-start 2026-01-01 --range-end 2026-03-31
readeck-cli bookmarks search --read-status unread --archived
readeck-cli bookmarks search --labels "python,security" --type article
readeck-cli bookmarks search --collection <id>
readeck-cli bookmarks export <id> --format md     # or pdf
```

`bookmarks search` filter options:

| Option | Type | Description |
|---|---|---|
| `--search` / `-s` | string | Full-text search |
| `--title` | string | Filter by title |
| `--author` | string | Filter by author |
| `--site` | string | Filter by site name or domain |
| `--type` | repeatable | `article`, `photo`, `video` |
| `--labels` | string | Labels, comma-separated |
| `--range-start` / `--range-end` | ISO 8601 | Date range |
| `--read-status` | repeatable | `unread`, `reading`, `read` |
| `--archived` / `--no-archived` | flag | Archived status |
| `--marked` / `--no-marked` | flag | Marked/favourite |
| `--has-labels` / `--no-has-labels` | flag | Has labels or not |
| `--loaded` / `--no-loaded` | flag | Loaded state |
| `--errors` / `--no-errors` | flag | Error state |
| `--collection` | string | Collection ID |
| `--id` | string | Bookmark ID(s) |
| `--sort` | repeatable | `created`, `-created`, `title`, `-title`, `domain`, `site`, `duration`, `published` |
| `--limit` / `-l` | integer | Max results (default: 100) |

### Labels

```bash
readeck-cli labels list
readeck-cli labels get <id>
readeck-cli labels create <name>
readeck-cli labels update <id> --name <new-name>
readeck-cli labels delete <id>
```

### Collections

```bash
readeck-cli collections list
readeck-cli collections get <id>
readeck-cli collections create <name>
readeck-cli collections update <id> --name <new-name>
readeck-cli collections delete <id>
```

### Highlights

```bash
readeck-cli highlights list
readeck-cli highlights list --bookmark <id>
readeck-cli highlights delete <id>
```

### Profile

```bash
readeck-cli profile show
```

## Global options

Every command accepts:

| Flag | Env var | Description |
|------|---------|-------------|
| `--url` | `READECK_URL` | Override configured URL |
| `--token` | `READECK_TOKEN` | Override configured token |
| `--output [table\|json]` | — | Output format (default: table) |

## Development

```bash
uv sync --group dev

uv run pytest tests/unit tests/integration -v   # unit + integration tests
uv run pytest tests/e2e -v                       # E2E (requires READECK_E2E=1 + real instance)

uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
uv run ty check src/
```

Pre-commit hooks (via [prek](https://prek.j178.dev)):

```bash
prek install
prek run --all-files
```

## License

MIT
