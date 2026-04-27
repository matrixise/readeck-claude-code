# tests/unit/test_output.py
import json
from io import StringIO

from rich.console import Console

from readeck_cli.output import OutputFormat, render_json, render_table


def test_render_json_returns_valid_json() -> None:
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
