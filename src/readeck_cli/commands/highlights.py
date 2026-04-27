# src/readeck_cli/commands/highlights.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.models.highlight import Highlight
from readeck_cli.output import (
    OutputFormat,
    print_error,
    print_success,
    render_json,
    render_table,
)
from readeck_cli.services.highlights import HighlightService

app = typer.Typer(help="Manage highlights")


def _make_service(
    url: str | None, token: str | None
) -> tuple[ReadeckClient, HighlightService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    client = ReadeckClient(config.url, config.token)
    return client, HighlightService(client)


@app.command("list")
def list_highlights(
    bookmark: Annotated[
        str | None, typer.Option("--bookmark", "-b", help="Filter by bookmark ID")
    ] = None,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """List highlights (optionally filtered by bookmark)."""
    client, service = _make_service(url, token)

    async def _run() -> list[Highlight]:
        async with client:
            return await service.list(bookmark_id=bookmark)

    try:
        highlights = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

    if output == OutputFormat.JSON:
        render_json([h.model_dump(mode="json") for h in highlights])
    else:
        render_table(
            headers=["ID", "Bookmark", "Text", "Created"],
            rows=[
                [
                    h.id,
                    h.bookmark_id or "",
                    h.text[:80] + ("…" if len(h.text) > 80 else ""),
                    str(h.created.date()),
                ]
                for h in highlights
            ],
            title=f"Highlights ({len(highlights)})",
        )


@app.command("delete")
def delete_highlight(
    highlight_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a highlight."""
    if not confirm:
        typer.confirm(f"Delete highlight {highlight_id}?", abort=True)
    client, service = _make_service(url, token)

    async def _run() -> None:
        async with client:
            await service.delete(highlight_id)

    try:
        asyncio.run(_run())
        print_success(f"Highlight {highlight_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
