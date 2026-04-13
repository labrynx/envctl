"""CLI callbacks."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

import typer


def version_callback(value: bool | None) -> None:
    """Print the version and exit."""
    if not value:
        return

    try:
        resolved_version = version("envctl")
    except PackageNotFoundError:
        resolved_version = "unknown"

    typer.echo(f"envctl {resolved_version}")
    raise typer.Exit()
