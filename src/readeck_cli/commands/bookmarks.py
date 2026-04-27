from __future__ import annotations

import asyncio
import sys
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
        async with client:
            return await service.list_bookmarks(
                page=page, limit=limit, fetch_all=all_pages
            )

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
        async with client:
            return await service.get(bookmark_id)

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
        async with client:
            return await service.create(bookmark_url)

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
        async with client:
            return await service.update(bookmark_id, **updates)

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
        async with client:
            await service.delete(bookmark_id)

    try:
        asyncio.run(_run())
        print_success(f"Bookmark {bookmark_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


_SORT_VALUES = [
    "created",
    "-created",
    "domain",
    "-domain",
    "duration",
    "-duration",
    "published",
    "-published",
    "site",
    "-site",
    "title",
    "-title",
]
_TYPE_VALUES = ["article", "photo", "video"]
_READ_STATUS_VALUES = ["unread", "reading", "read"]


@app.command("search")
def search_bookmarks(
    search: Annotated[
        str | None, typer.Option("--search", "-s", help="Full-text search string")
    ] = None,
    title: Annotated[
        str | None, typer.Option("--title", help="Filter by bookmark title")
    ] = None,
    author: Annotated[
        str | None, typer.Option("--author", help="Filter by author name")
    ] = None,
    site: Annotated[
        str | None, typer.Option("--site", help="Filter by site name or domain")
    ] = None,
    type: Annotated[
        list[str] | None,
        typer.Option("--type", help="Filter by type (article, photo, video)"),
    ] = None,
    labels: Annotated[
        str | None, typer.Option("--labels", help="Filter by labels (comma-separated)")
    ] = None,
    is_loaded: Annotated[
        bool | None, typer.Option("--loaded/--no-loaded", help="Filter by loaded state")
    ] = None,
    has_errors: Annotated[
        bool | None,
        typer.Option("--errors/--no-errors", help="Filter by error state"),
    ] = None,
    has_labels: Annotated[
        bool | None,
        typer.Option("--has-labels/--no-has-labels", help="Filter by label presence"),
    ] = None,
    is_archived: Annotated[
        bool | None,
        typer.Option("--archived/--no-archived", help="Filter by archived status"),
    ] = None,
    is_marked: Annotated[
        bool | None,
        typer.Option("--marked/--no-marked", help="Filter by marked/favourite status"),
    ] = None,
    range_start: Annotated[
        str | None,
        typer.Option("--range-start", help="Date range start (ISO 8601)"),
    ] = None,
    range_end: Annotated[
        str | None, typer.Option("--range-end", help="Date range end (ISO 8601)")
    ] = None,
    read_status: Annotated[
        list[str] | None,
        typer.Option("--read-status", help="Read status: unread, reading, read"),
    ] = None,
    bookmark_id: Annotated[
        str | None, typer.Option("--id", help="Filter by bookmark ID(s)")
    ] = None,
    collection: Annotated[
        str | None, typer.Option("--collection", help="Filter by collection ID")
    ] = None,
    sort: Annotated[
        list[str] | None,
        typer.Option("--sort", help="Sort order, repeatable (e.g. -created, title)"),
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Max results to return")
    ] = 100,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Search and filter bookmarks."""
    _bool_flags = [is_loaded, has_errors, has_labels, is_archived, is_marked]
    _has_filter = any(
        [
            search,
            title,
            author,
            site,
            type,
            labels,
            range_start,
            range_end,
            read_status,
            bookmark_id,
            collection,
            sort,
            any(f is not None for f in _bool_flags),
        ]
    )
    if not _has_filter:
        print_error(
            "Provide at least one filter"
            " (e.g. --search, --title, --labels, --range-start, --archived)."
        )
        raise typer.Exit(1) from None

    client, service = _make_service(url, token)

    async def _run() -> list[Bookmark]:
        async with client:
            return await service.search(
                search=search,
                title=title,
                author=author,
                site=site,
                type=type,
                labels=labels,
                is_loaded=is_loaded,
                has_errors=has_errors,
                has_labels=has_labels,
                is_archived=is_archived,
                is_marked=is_marked,
                range_start=range_start,
                range_end=range_end,
                read_status=read_status,
                id=bookmark_id,
                collection=collection,
                sort=sort,
                limit=limit,
            )

    try:
        bookmarks = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

    if output == OutputFormat.JSON:
        render_json([bm.model_dump(mode="json") for bm in bookmarks])
    else:
        filters = ", ".join(
            filter(
                None,
                [
                    f"search={search!r}" if search else None,
                    f"title={title!r}" if title else None,
                    f"author={author!r}" if author else None,
                    f"site={site!r}" if site else None,
                    f"range={range_start}..{range_end}"
                    if range_start or range_end
                    else None,
                ],
            )
        )
        suffix = f" — {filters}" if filters else ""
        render_table(
            headers=["ID", "Title", "URL", "Archived", "Read (min)", "Labels"],
            rows=[_bookmark_row(bm) for bm in bookmarks],
            title=f"Search results ({len(bookmarks)}){suffix}",
        )


@app.command("export")
def export_bookmark(
    bookmark_id: Annotated[str, typer.Argument()],
    fmt: Annotated[str, typer.Option("--format", "-f", help="md or pdf")] = "md",
    dest: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output file path")
    ] = None,
    stdout: Annotated[
        bool, typer.Option("--stdout", help="Write to stdout instead of a file")
    ] = False,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Export a bookmark as md or pdf."""
    client, service = _make_service(url, token)

    async def _run() -> bytes:
        async with client:
            return await service.export(bookmark_id, fmt=fmt)

    try:
        content = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

    if stdout:
        sys.stdout.buffer.write(content)
        return

    out_path = dest or Path(f"{bookmark_id}.{fmt}")
    out_path.write_bytes(content)
    print_success(f"Exported to {out_path}")
