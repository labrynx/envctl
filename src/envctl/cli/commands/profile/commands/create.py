"""Profile create command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.services.profile_service import run_profile_create
from envctl.utils.output import print_kv, print_success, print_warning

PROFILE_ARGUMENT = typer.Argument(...)


@handle_errors
@requires_writable_runtime("profile create")
@text_output_only("profile create")
def profile_create_command(
    profile: str = PROFILE_ARGUMENT,
) -> None:
    """Create one explicit empty profile."""
    _context, result = run_profile_create(profile)

    if result.created:
        print_success(f"Created profile '{result.profile}'")
    else:
        print_warning(f"Profile '{result.profile}' already exists")

    print_kv("profile", result.profile)
    print_kv("path", str(result.path))
