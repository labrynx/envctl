"""Terminal output helpers."""

from __future__ import annotations

import typer


def print_success(message: str) -> None:
    """Print a success message."""
    typer.echo(f"[OK] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    typer.echo(f"[WARN] {message}")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    typer.echo(message, err=True)


def print_kv(key: str, value: str) -> None:
    """Print a key/value pair."""
    typer.echo(f"{key}: {value}")
