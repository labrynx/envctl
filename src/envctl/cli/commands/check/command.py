"""Check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_resolution
from envctl.services.check_service import run_check
from envctl.utils.output import print_success, print_warning


@handle_errors
def check_command() -> None:
    """Validate the resolved environment against the contract."""
    _context, report = run_check()
    render_resolution(report)

    if report.is_valid and not report.unknown_keys:
        print_success("Environment contract satisfied")
        return

    if report.is_valid:
        print_warning("Environment is valid, but the vault contains unknown keys")
        raise typer.Exit(code=1)

    raise typer.Exit(code=1)
