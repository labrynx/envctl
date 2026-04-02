"""CLI callbacks."""

from __future__ import annotations

import typer

from envctl import __version__


def version_callback(value: bool) -> None:
    """Print the version and exit."""
    if value:
        typer.echo(f"envctl {__version__}")
        raise typer.Exit()
