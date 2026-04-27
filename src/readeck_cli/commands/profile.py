# src/readeck_cli/commands/profile.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config
from readeck_cli.models.profile import UserProfile
from readeck_cli.output import OutputFormat, print_error, render_json, render_table
from readeck_cli.services.profile import ProfileService

app = typer.Typer(help="User profile")


@app.command("show")
def show_profile(
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
    output: Annotated[
        OutputFormat, typer.Option("--output", "-o")
    ] = OutputFormat.TABLE,
) -> None:
    """Show current user profile."""
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from e

    async def _get() -> UserProfile:
        async with ReadeckClient(config.url, config.token) as client:
            return await ProfileService(client).get()

    try:
        profile = asyncio.run(_get())
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e

    if output == OutputFormat.JSON:
        render_json(profile.model_dump(mode="json"))
    else:
        render_table(
            headers=["Field", "Value"],
            rows=[
                ["Username", profile.username],
                ["Email", profile.email or ""],
            ],
            title="Profile",
        )
