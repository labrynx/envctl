"""Profile list command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_profile_list_result
from envctl.cli.runtime import get_active_profile
from envctl.services.profile_service import run_profile_list


@handle_errors
@text_output_only("profile list")
def profile_list_command() -> None:
    """List available profiles."""
    _context, result = run_profile_list(get_active_profile())

    render_profile_list_result(
        active_profile=result.active_profile,
        profiles=result.profiles,
    )
