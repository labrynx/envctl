"""Presenters for structured state errors."""

from __future__ import annotations

import typer

from envctl.domain.error_diagnostics import StateDiagnostics


def render_state_error(
    diagnostics: StateDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured state error to stderr."""
    typer.echo(f"Error: {message}", err=True)
    typer.echo(err=True)
    typer.echo(f"path: {diagnostics.path}", err=True)
    if diagnostics.field is not None:
        typer.echo(f"field: {diagnostics.field}", err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)
