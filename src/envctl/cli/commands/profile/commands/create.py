"""Profile create command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters.profile_presenter import render_profile_create_result

PROFILE_ARGUMENT = typer.Argument(...)


@handle_errors
@requires_writable_runtime("profile create")
@text_output_only("profile create")
def profile_create_command(
    profile: str = PROFILE_ARGUMENT,
) -> None:
    """Create one explicit empty profile."""
    from envctl.services.profile_service import run_profile_create

    _context, result = run_profile_create(profile)

    render_profile_create_result(
        profile=result.profile,
        path=result.path,
        created=result.created,
    )
