# src/readeck_cli/commands/collections.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.models.collection import Collection
from readeck_cli.output import (
    OutputFormat,
    print_error,
    print_success,
    render_json,
    render_table,
)
from readeck_cli.services.collections import CollectionService

app = typer.Typer(help="Manage collections")


def _make_service(
    url: str | None, token: str | None
) -> tuple[ReadeckClient, CollectionService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    client = ReadeckClient(config.url, config.token)
    return client, CollectionService(client)


@app.command("list")
def list_collections(
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """List all collections."""
    client, service = _make_service(url, token)

    async def _run() -> list[Collection]:
        async with client:
            return await service.list()

    try:
        collections = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

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
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Get a collection by ID."""
    client, service = _make_service(url, token)

    async def _run() -> Collection:
        async with client:
            return await service.get(collection_id)

    try:
        col = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None

    if output == OutputFormat.JSON:
        render_json(col.model_dump(mode="json"))
    else:
        render_table(
            headers=["Field", "Value"],
            rows=[["ID", col.id], ["Title", col.title], ["Created", str(col.created)]],
        )


@app.command("create")
def create_collection(
    title: Annotated[str, typer.Argument()],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Create a new collection."""
    client, service = _make_service(url, token)

    async def _run() -> Collection:
        async with client:
            return await service.create(title)

    try:
        col = asyncio.run(_run())
        print_success(f"Collection '{col.title}' created (id: {col.id})")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


@app.command("update")
def update_collection(
    collection_id: Annotated[str, typer.Argument()],
    title: Annotated[str, typer.Option("--title")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Rename a collection."""
    client, service = _make_service(url, token)

    async def _run() -> Collection:
        async with client:
            return await service.update(collection_id, title=title)

    try:
        col = asyncio.run(_run())
        print_success(f"Collection updated to '{col.title}'")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None


@app.command("delete")
def delete_collection(
    collection_id: Annotated[str, typer.Argument()],
    confirm: Annotated[bool, typer.Option("--yes", "-y")] = False,
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Delete a collection."""
    if not confirm:
        typer.confirm(f"Delete collection {collection_id}?", abort=True)
    client, service = _make_service(url, token)

    async def _run() -> None:
        async with client:
            await service.delete(collection_id)

    try:
        asyncio.run(_run())
        print_success(f"Collection {collection_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
