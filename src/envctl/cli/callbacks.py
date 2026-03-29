"""CLI callbacks and bridges."""

from __future__ import annotations

import getpass

import typer

from envctl import __version__


def version_callback(value: bool) -> None:
    """Print the version and exit."""
    if value:
        typer.echo(f"envctl {__version__}")
        raise typer.Exit()


def typer_prompt(message: str, secret: bool, default: str | None) -> str:
    """Bridge prompts from services to Typer."""
    suffix = f" [{default}]" if default is not None else ""
    full_message = f"{message}{suffix}"
    if secret:
        value = getpass.getpass(f"{full_message}: ")
        return value if value else (default or "")
    return typer.prompt(full_message, default=default or "", show_default=False)


def typer_confirm(message: str, default: bool = False) -> bool:
    """Bridge confirmations from services to Typer."""
    return typer.confirm(message, default=default, show_default=True)
