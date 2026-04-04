"""Presenters for structured configuration errors."""

from __future__ import annotations

import typer

from envctl.services.error_diagnostics import ConfigDiagnostics


def render_config_error(
    diagnostics: ConfigDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured config error to stderr."""
    typer.echo(f"Error: {message}", err=True)

    has_details = any(
        value is not None
        for value in (
            diagnostics.path,
            diagnostics.source_label,
            diagnostics.key,
            diagnostics.field,
            diagnostics.value,
        )
    )
    if has_details:
        typer.echo(err=True)

    if diagnostics.path is not None:
        typer.echo(f"path: {diagnostics.path}", err=True)
    if diagnostics.source_label is not None:
        typer.echo(f"source: {diagnostics.source_label}", err=True)
    if diagnostics.key is not None:
        typer.echo(f"key: {diagnostics.key}", err=True)
    if diagnostics.field is not None:
        typer.echo(f"field: {diagnostics.field}", err=True)
    if diagnostics.value is not None:
        typer.echo(f"value: {diagnostics.value}", err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)
