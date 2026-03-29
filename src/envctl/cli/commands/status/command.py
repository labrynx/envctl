"""Status command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_status
from envctl.services.status_service import run_status


@handle_errors
def status_command() -> None:
    """Show the current project status."""
    render_status(run_status())
