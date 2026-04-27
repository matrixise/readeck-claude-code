# src/readeck_cli/commands/labels.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
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
    try:
        labels = asyncio.run(service.list())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json(
            [{"id": lbl.id, "label": lbl.label, "count": lbl.count} for lbl in labels]
        )
    else:
        render_table(
            headers=["ID", "Label", "Count"],
            rows=[[lbl.id, lbl.label, str(lbl.count or 0)] for lbl in labels],
            title=f"Labels ({len(labels)})",
        )


@app.command("get")
def get_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Get a label by ID."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.get(label_id))
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    finally:
        asyncio.run(client.aclose())

    if output == OutputFormat.JSON:
        render_json({"id": label.id, "label": label.label, "count": label.count})
    else:
        render_table(
            headers=["ID", "Label", "Count"],
            rows=[[label.id, label.label, str(label.count or 0)]],
        )


@app.command("create")
def create_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Create a new label."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.create(name))
        print_success(f"Label '{label.label}' created (id: {label.id})")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    finally:
        asyncio.run(client.aclose())


@app.command("update")
def update_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    name: Annotated[str, typer.Option("--name", help="New name")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Rename a label."""
    client, service = _make_service(url, token)
    try:
        label = asyncio.run(service.update(label_id, name=name))
        print_success(f"Label updated to '{label.label}'")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    finally:
        asyncio.run(client.aclose())


@app.command("delete")
def delete_label(
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    confirm: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation")
    ] = False,
) -> None:
    """Delete a label."""
    if not confirm:
        typer.confirm(f"Delete label {label_id}?", abort=True)
    client, service = _make_service(url, token)
    try:
        asyncio.run(service.delete(label_id))
        print_success(f"Label {label_id} deleted.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e
    finally:
        asyncio.run(client.aclose())
