# src/readeck_cli/commands/auth.py
from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.config import load_config, remove_token, save_config
from readeck_cli.models.auth import TokenInfo
from readeck_cli.output import print_error, print_success, render_table
from readeck_cli.services.auth import AuthService

app = typer.Typer(help="Authentication commands")


@app.command()
def login(
    url: Annotated[str | None, typer.Option(prompt=True, help="Readeck URL")] = None,
    username: Annotated[str | None, typer.Option(prompt=True, help="Username")] = None,
    password: Annotated[
        str | None, typer.Option(prompt=True, hide_input=True, help="Password")
    ] = None,
) -> None:
    """Login and save token to config."""
    assert url and username and password
    try:
        data = asyncio.run(ReadeckClient.create_token(url, username, password))
        token = TokenInfo.model_validate(data)
        save_config(url=url, token=token.token)
        print_success(f"Logged in as {username}. Token saved to config.")
    except ReadeckAPIError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command()
def logout() -> None:
    """Remove token from config."""
    remove_token()
    print_success("Token removed from config.")


@app.command()
def status(
    url: Annotated[str | None, typer.Option(envvar="READECK_URL")] = None,
    token: Annotated[str | None, typer.Option(envvar="READECK_TOKEN")] = None,
) -> None:
    """Show configured URL and validate token."""
    try:
        config = load_config(url=url, token=token)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1) from e

    async def _check() -> bool:
        async with ReadeckClient(config.url, config.token) as client:
            return await AuthService(client).validate_token()

    valid = asyncio.run(_check())
    status_str = "✓ valid" if valid else "✗ invalid"
    render_table(
        headers=["URL", "Token", "Status"],
        rows=[[config.url, config.token[:8] + "…", status_str]],
        title="Auth Status",
    )


token_app = typer.Typer(help="Token management")
app.add_typer(token_app, name="token")


@token_app.command("set")
def token_set(
    value: Annotated[str, typer.Argument(help="API token")],
    url: Annotated[
        str | None, typer.Option(envvar="READECK_URL", help="Readeck URL")
    ] = None,
) -> None:
    """Save a token manually without going through login."""
    try:
        config = load_config(url=url, token="placeholder")
        save_config(url=config.url, token=value)
    except ValueError:
        if not url:
            print_error("Provide --url or set READECK_URL.")
            raise typer.Exit(1) from None
        save_config(url=url, token=value)
    print_success("Token saved to config.")
