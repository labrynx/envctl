"""Profile create command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_profile_create_output
from envctl.cli.runtime import is_json_output

PROFILE_ARGUMENT = typer.Argument(...)


@handle_errors
@requires_writable_runtime("profile create")
def profile_create_command(
    profile: str = PROFILE_ARGUMENT,
) -> None:
    """Create one explicit empty profile."""
    from envctl.services.profile_service import run_profile_create

    _context, result = run_profile_create(profile)

    present(
        build_profile_create_output(
            profile=result.profile,
            path=result.path,
            created=result.created,
        ),
        output_format="json" if is_json_output() else "text",
    )
