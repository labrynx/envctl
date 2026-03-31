"""Unset command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import render_unset_result
from envctl.cli.runtime import get_active_profile
from envctl.services.unset_service import run_unset


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

    render_unset_result(
        key=key,
        profile=active_profile,
        profile_path=profile_path,
        removed=removed,
    )
