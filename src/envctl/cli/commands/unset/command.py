"""Unset command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.runtime import get_active_profile
from envctl.services.unset_service import run_unset
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
@requires_writable_runtime("unset")
def unset_command(
    key: str = typer.Argument(...),
) -> None:
    """Remove one local value from the active profile."""
    _context, active_profile, profile_path, removed = run_unset(
        key=key,
        active_profile=get_active_profile(),
    )

    if removed:
        print_success(f"Unset '{key}' in profile '{active_profile}'")
    else:
        print_warning(f"'{key}' was not set in profile '{active_profile}'")

    print_kv("profile", active_profile)
    print_kv("vault_values", str(profile_path))
