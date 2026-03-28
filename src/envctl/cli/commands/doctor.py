"""Doctor command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_doctor_checks
from envctl.services.doctor_service import run_doctor


@handle_errors
def doctor_command() -> None:
    """Run local read-only diagnostics."""
    has_failures = render_doctor_checks(run_doctor())
    if has_failures:
        raise typer.Exit(code=1)
