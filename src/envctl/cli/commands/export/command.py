"""Export command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_export_output
from envctl.cli.runtime import get_active_profile
from envctl.services.export_service import run_export


@handle_errors
@text_output_only("export")
def export_command() -> None:
    """Print the resolved environment as shell export lines."""
    _context, active_profile, rendered = run_export(get_active_profile())
    render_export_output(profile=active_profile, rendered=rendered)
