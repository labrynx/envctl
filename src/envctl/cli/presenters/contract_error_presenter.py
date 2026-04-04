"""Presenters for structured contract errors."""

from __future__ import annotations

import typer

from envctl.services.error_diagnostics import ContractDiagnostics


def render_contract_error(
    diagnostics: ContractDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured contract error to stderr."""
    typer.echo(f"Error: {message}", err=True)
    typer.echo(err=True)
    typer.echo(f"path: {diagnostics.path}", err=True)
    if diagnostics.field is not None:
        typer.echo(f"field: {diagnostics.field}", err=True)
    if diagnostics.key is not None:
        typer.echo(f"key: {diagnostics.key}", err=True)

    if diagnostics.issues:
        typer.echo(err=True)
        typer.echo("Contract issues", err=True)
        for issue in diagnostics.issues:
            typer.echo(f"  - {issue.field}: {issue.detail}", err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)
