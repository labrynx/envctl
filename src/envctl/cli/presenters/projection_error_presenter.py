"""Presenters for projection validation failures."""

from __future__ import annotations

import typer

from envctl.cli.presenters.resolution_presenter import build_resolution_problem_lines
from envctl.services.error_diagnostics import ProjectionValidationDiagnostics


def render_projection_validation_failure(
    diagnostics: ProjectionValidationDiagnostics,
    *,
    message: str,
) -> None:
    """Render a projection validation failure to stderr."""
    typer.echo(f"Error: {message}", err=True)
    typer.echo(err=True)
    typer.echo(f"profile: {diagnostics.active_profile}", err=True)
    if diagnostics.selected_group is not None:
        typer.echo(f"group: {diagnostics.selected_group}", err=True)

    for line in build_resolution_problem_lines(
        diagnostics.report,
        unknown_keys_title="Unknown keys in vault for the current contract",
    ):
        typer.echo(line, err=True)

    if diagnostics.suggested_actions:
        typer.echo(err=True)
        typer.echo("Next steps", err=True)
        for action in diagnostics.suggested_actions:
            typer.echo(f"  - Run `{action}`", err=True)
