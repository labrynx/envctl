"""Status command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_status_report
from envctl.services.status_service import run_status


@handle_errors
def status_command() -> None:
    """Show the current repository envctl status."""
    report = run_status()
    render_status_report(report)
