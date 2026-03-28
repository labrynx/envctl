"""Inspect command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_resolution
from envctl.services.inspect_service import run_inspect


@handle_errors
def inspect_command() -> None:
    """Inspect the resolved environment."""
    _context, report = run_inspect()
    render_resolution(report)
