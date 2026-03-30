"""Set command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.runtime import get_active_profile
from envctl.services.set_service import run_set
from envctl.utils.output import print_kv, print_success


@handle_errors
@requires_writable_runtime("set")
def set_command(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
) -> None:
    """Set one local value in the active profile."""
    _context, active_profile, profile_path = run_set(
        key=key,
        value=value,
        active_profile=get_active_profile(),
    )

    print_success(f"Set '{key}' in profile '{active_profile}'")
    print_kv("profile", active_profile)
    print_kv("vault_values", str(profile_path))
