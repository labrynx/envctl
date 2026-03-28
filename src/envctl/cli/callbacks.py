"""CLI callbacks and bridges."""

from __future__ import annotations

import typer

from envctl import __version__


def version_callback(value: bool) -> None:
    """Print version and exit if --version is passed."""
    if value:
        typer.echo(f"envctl {__version__}")
        raise typer.Exit()


def typer_confirm(message: str, default: bool) -> bool:
    """Bridge confirmation prompts from services to Typer."""
    return typer.confirm(message, default=default)
