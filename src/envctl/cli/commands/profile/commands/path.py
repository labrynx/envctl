"""Profile path command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters.profile_presenter import render_profile_path_result
from envctl.cli.runtime import get_active_profile

PROFILE_ARGUMENT = typer.Argument(None)


@handle_errors
@text_output_only("profile path")
def profile_path_command(
    profile: str | None = PROFILE_ARGUMENT,
) -> None:
    """Show the filesystem path for one profile."""
    from envctl.services.profile_service import run_profile_path

    _context, result = run_profile_path(
        profile=profile,
        active_profile=get_active_profile(),
    )

    render_profile_path_result(
        profile=result.profile,
        path=result.path,
    )
