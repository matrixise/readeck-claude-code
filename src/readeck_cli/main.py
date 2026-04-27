from __future__ import annotations

import typer

app = typer.Typer(
    name="readeck-cli",
    help="CLI for Readeck read-it-later service.",
    no_args_is_help=True,
)

if __name__ == "__main__":
    app()
