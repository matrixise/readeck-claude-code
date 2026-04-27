# src/readeck_cli/output.py
from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

from rich.console import Console
from rich.table import Table

_default_console = Console()


class OutputFormat(StrEnum):
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
