from __future__ import annotations

import typer

from readeck_cli.commands import (
    auth,
    bookmarks,
    collections,
    highlights,
    labels,
    profile,
)

app = typer.Typer(
    name="readeck-cli",
    help="CLI for Readeck read-it-later service.",
    no_args_is_help=True,
)

app.add_typer(auth.app, name="auth")
app.add_typer(bookmarks.app, name="bookmarks")
app.add_typer(labels.app, name="labels")
app.add_typer(collections.app, name="collections")
app.add_typer(highlights.app, name="highlights")
app.add_typer(profile.app, name="profile")

if __name__ == "__main__":
    app()
