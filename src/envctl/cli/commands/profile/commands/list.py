"""Profile list command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.runtime import get_active_profile
from envctl.services.profile_service import run_profile_list
from envctl.utils.output import print_kv


@handle_errors
@text_output_only("profile list")
def profile_list_command() -> None:
    """List available profiles."""
    _context, result = run_profile_list(get_active_profile())

    print_kv("active_profile", result.active_profile)
    print_kv("profiles", ", ".join(result.profiles))
