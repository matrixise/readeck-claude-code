from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.models.bookmark import Bookmark, BookmarkUpdated
from readeck_cli.output import (
    OutputFormat,
    print_error,
    print_success,
    render_json,
    render_table,
)
from readeck_cli.services.bookmarks import BookmarkService

app = typer.Typer(help="Manage bookmarks")


def _make_service(
    url: str | None, token: str | None
) -> tuple[ReadeckClient, BookmarkService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    client = ReadeckClient(config.url, config.token)
    return client, BookmarkService(client)


def _bookmark_row(bm: Bookmark) -> list[str]:
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
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """List bookmarks."""
    client, service = _make_service(url, token)

    async def _run() -> tuple[list[Bookmark], int]:
        try:
            return await service.list(page=page, limit=limit, fetch_all=all_pages)
        finally:
            await client.aclose()

    try:
        bookmarks, total = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

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
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Get a bookmark by ID."""
    client, service = _make_service(url, token)

    async def _run() -> Bookmark:
        try:
            return await service.get(bookmark_id)
        finally:
            await client.aclose()

    try:
        bm = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

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
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Add a new bookmark."""
    client, service = _make_service(url, token)

    async def _run() -> str:
        try:
            return await service.create(bookmark_url)
        finally:
            await client.aclose()

    try:
        bookmark_id = asyncio.run(_run())
        print_success(f"Bookmark submitted (id: {bookmark_id})")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


@app.command("update")
def update_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    title: Annotated[str | None, typer.Option("--title")] = None,
    labels: Annotated[
        str | None, typer.Option("--labels", help="Comma-separated labels")
    ] = None,
    is_archived: Annotated[
        bool | None, typer.Option("--archived/--no-archived")
    ] = None,
    is_marked: Annotated[bool | None, typer.Option("--marked/--no-marked")] = None,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Update a bookmark."""
    updates: dict[str, object] = {}
    if title is not None:
        updates["title"] = title
    if labels is not None:
        updates["labels"] = [lbl.strip() for lbl in labels.split(",")]
    if is_archived is not None:
        updates["is_archived"] = is_archived
    if is_marked is not None:
        updates["is_marked"] = is_marked
    if not updates:
        print_error("No fields to update.")
        raise typer.Exit(1) from None

    client, service = _make_service(url, token)

    async def _run() -> BookmarkUpdated:
        try:
            return await service.update(bookmark_id, **updates)
        finally:
            await client.aclose()

    try:
        bm = asyncio.run(_run())
        print_success(f"Bookmark {bm.id} updated.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


@app.command("delete")
def delete_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a bookmark."""
    if not confirm:
        typer.confirm(f"Delete bookmark {bookmark_id}?", abort=True)
    client, service = _make_service(url, token)

    async def _run() -> None:
        try:
            await service.delete(bookmark_id)
        finally:
            await client.aclose()

    try:
        asyncio.run(_run())
        print_success(f"Bookmark {bookmark_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


@app.command("search")
def search_bookmarks(
    query: Annotated[str, typer.Argument()],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Full-text search bookmarks."""
    client, service = _make_service(url, token)

    async def _run() -> list[Bookmark]:
        try:
            return await service.search(query)
        finally:
            await client.aclose()

    try:
        bookmarks = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

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
    dest: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output file path")
    ] = None,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Export a bookmark as epub or pdf."""
    client, service = _make_service(url, token)

    async def _run() -> bytes:
        try:
            return await service.export(bookmark_id, fmt=fmt)
        finally:
            await client.aclose()

    try:
        content = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

    out_path = dest or Path(f"{bookmark_id}.{fmt}")
    out_path.write_bytes(content)
    print_success(f"Exported to {out_path}")
