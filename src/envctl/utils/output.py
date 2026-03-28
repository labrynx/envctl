"""Console output helpers."""

from __future__ import annotations

import typer


def print_success(message: str) -> None:
    """Print a success message."""
    typer.secho(message, fg=typer.colors.GREEN)


def print_warning(message: str) -> None:
    """Print a warning message."""
    typer.secho(message, fg=typer.colors.YELLOW)


def print_error(message: str) -> None:
    """Print an error message."""
    typer.secho(message, fg=typer.colors.RED, err=True)


def print_kv(key: str, value: str) -> None:
    """Print a simple key/value line."""
    typer.echo(f"{key}: {value}")
