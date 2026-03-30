"""Profile remove command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.services.profile_service import run_profile_remove
from envctl.utils.output import print_kv, print_success, print_warning

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
        approved = typer_confirm(
            f"Remove profile '{profile}'?",
            default=False,
        )
        if not approved:
            print_warning("Nothing was changed.")
            return

    _context, result = run_profile_remove(profile)

    if result.removed:
        print_success(f"Removed profile '{result.profile}'")
    else:
        print_warning(f"Profile '{result.profile}' does not exist")

    print_kv("profile", result.profile)
    print_kv("path", str(result.path))
