# src/readeck_cli/commands/labels.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.models.label import Label
from readeck_cli.output import (
    OutputFormat,
    print_error,
    print_success,
    render_json,
    render_table,
)
from readeck_cli.services.labels import LabelService

app = typer.Typer(help="Manage labels")


def _make_service(
    url: str | None, token: str | None
) -> tuple[ReadeckClient, LabelService]:
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    client = ReadeckClient(config.url, config.token)
    return client, LabelService(client)


@app.command("list")
def list_labels(
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """List all labels."""
    client, service = _make_service(url, token)

    async def _run() -> list[Label]:
        try:
            return await service.list()
        finally:
            await client.aclose()

    try:
        labels = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e

    if output == OutputFormat.JSON:
        render_json([{"name": lbl.name, "count": lbl.count} for lbl in labels])
    else:
        render_table(
            headers=["Name", "Count"],
            rows=[[lbl.name, str(lbl.count or 0)] for lbl in labels],
            title=f"Labels ({len(labels)})",
        )


@app.command("get")
def get_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Get a label by name."""
    client, service = _make_service(url, token)

    async def _run() -> Label:
        try:
            return await service.get(name)
        finally:
            await client.aclose()

    try:
        label = asyncio.run(_run())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e

    if output == OutputFormat.JSON:
        render_json({"name": label.name, "count": label.count})
    else:
        render_table(
            headers=["Name", "Count"],
            rows=[[label.name, str(label.count or 0)]],
        )


@app.command("create")
def create_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Create a new label."""
    client, service = _make_service(url, token)

    async def _run() -> Label:
        try:
            return await service.create(name)
        finally:
            await client.aclose()

    try:
        label = asyncio.run(_run())
        print_success(f"Label '{label.name}' created")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command("update")
def update_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    new_name: Annotated[str, typer.Option("--name", help="New name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Rename a label."""
    client, service = _make_service(url, token)

    async def _run() -> Label:
        try:
            return await service.update(name, new_name=new_name)
        finally:
            await client.aclose()

    try:
        label = asyncio.run(_run())
        print_success(f"Label updated to '{label.name}'")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command("delete")
def delete_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    confirm: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation")
    ] = False,
) -> None:
    """Delete a label."""
    if not confirm:
        typer.confirm(f"Delete label '{name}'?", abort=True)
    client, service = _make_service(url, token)

    async def _run() -> None:
        try:
            await service.delete(name)
        finally:
            await client.aclose()

    try:
        asyncio.run(_run())
        print_success(f"Label '{name}' deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
