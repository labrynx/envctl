"""Profile remove command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.common import cancelled_output
from envctl.cli.presenters.outputs.actions import build_profile_remove_output
from envctl.cli.prompts.confirmation_prompts import build_profile_remove_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import is_json_output
from envctl.domain.runtime import OutputFormat

PROFILE_ARGUMENT = typer.Argument(...)
YES_OPTION = typer.Option(
    False,
    "--yes",
    help="Skip confirmation.",
)


@handle_errors
@requires_writable_runtime("profile remove")
def profile_remove_command(
    profile: str = PROFILE_ARGUMENT,
    yes: bool = YES_OPTION,
) -> None:
    """Remove one explicit profile."""
    output_format: OutputFormat = OutputFormat.JSON if is_json_output() else OutputFormat.TEXT

    if not yes:
        approved = confirm(
            message=build_profile_remove_confirmation_message(profile),
            default=False,
        )
        if not approved:
            present(
                cancelled_output(
                    kind="profile_remove",
                    profile=profile,
                ),
                output_format=output_format,
            )
            return

    from envctl.services.profile_service import run_profile_remove

    _context, result = run_profile_remove(profile)

    present(
        build_profile_remove_output(
            profile=result.profile,
            path=result.path,
            removed=result.removed,
        ),
        output_format=output_format,
    )
