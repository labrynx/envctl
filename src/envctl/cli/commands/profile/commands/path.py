"""Profile path command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_profile_path_output
from envctl.cli.runtime import get_active_profile, is_json_output

PROFILE_ARGUMENT = typer.Argument(None)


@handle_errors
def profile_path_command(
    profile: str | None = PROFILE_ARGUMENT,
) -> None:
    """Show the filesystem path for one profile."""
    from envctl.services.profile_service import run_profile_path

    _context, result = run_profile_path(
        profile=profile,
        active_profile=get_active_profile(),
    )

    present(
        build_profile_path_output(
            profile=result.profile,
            path=result.path,
        ),
        output_format="json" if is_json_output() else "text",
    )
