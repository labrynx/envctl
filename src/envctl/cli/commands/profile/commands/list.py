"""Profile list command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_profile_list_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
def profile_list_command() -> None:
    """List available profiles."""
    from envctl.services.profile_service import run_profile_list

    _context, result = run_profile_list(get_active_profile())

    present(
        build_profile_list_output(
            active_profile=result.active_profile,
            profiles=result.profiles,
        ),
        output_format="json" if is_json_output() else "text",
    )
