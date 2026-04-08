"""Presenters for projection validation failures."""

from __future__ import annotations

import typer

from envctl.cli.presenters.common import (
    print_action_list,
    print_error_title,
    print_kv_line,
    print_section,
)
from envctl.cli.presenters.resolution_presenter import build_resolution_problem_lines
from envctl.domain.error_diagnostics import ProjectionValidationDiagnostics


def render_projection_validation_failure(
    diagnostics: ProjectionValidationDiagnostics,
    *,
    message: str,
) -> None:
    """Render a projection validation failure to stderr."""
    print_error_title(message)
    print_section("Context", err=True)
    print_kv_line("profile", diagnostics.active_profile, err=True)
    print_kv_line("scope", diagnostics.selection.describe(), err=True)

    print_section("Problems", err=True)
    for line in build_resolution_problem_lines(
        diagnostics.report,
        unknown_keys_title="Unknown keys in vault for the current contract",
    ):
        typer.echo(line, err=True)

    print_action_list(diagnostics.suggested_actions, err=True)
