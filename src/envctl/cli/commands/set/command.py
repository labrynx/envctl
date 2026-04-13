"""Set command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters.action_presenter import render_set_result
from envctl.cli.runtime import get_active_profile


@handle_errors
@requires_writable_runtime("set")
@text_output_only("set")
def set_command(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
) -> None:
    """Set one local value in the active profile."""
    from envctl.services.set_service import run_set

    _context, active_profile, profile_path = run_set(
        key=key,
        value=value,
        active_profile=get_active_profile(),
    )

    render_set_result(
        key=key,
        profile=active_profile,
        profile_path=profile_path,
    )
