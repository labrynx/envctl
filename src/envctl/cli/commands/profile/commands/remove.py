"""Profile remove command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters.profile_presenter import render_profile_remove_result
from envctl.cli.prompts.confirmation_prompts import build_profile_remove_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.utils.output import print_cancelled

PROFILE_ARGUMENT = typer.Argument(...)
YES_OPTION = typer.Option(
    False,
    "--yes",
    help="Skip confirmation.",
)


@handle_errors
@requires_writable_runtime("profile remove")
@text_output_only("profile remove")
def profile_remove_command(
    profile: str = PROFILE_ARGUMENT,
    yes: bool = YES_OPTION,
) -> None:
    """Remove one explicit profile."""
    if not yes:
        approved = confirm(
            message=build_profile_remove_confirmation_message(profile),
            default=False,
        )
        if not approved:
            print_cancelled()
            return

    from envctl.services.profile_service import run_profile_remove

    _context, result = run_profile_remove(profile)

    render_profile_remove_result(
        profile=result.profile,
        path=result.path,
        removed=result.removed,
    )
