"""Unset command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_unset_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
@requires_writable_runtime("unset")
def unset_command(
    key: str = typer.Argument(...),
) -> None:
    """Remove one local value from the active profile."""
    from envctl.services.unset_service import run_unset

    _context, active_profile, profile_path, removed = run_unset(
        key=key,
        active_profile=get_active_profile(),
    )

    output = build_unset_output(
        key=key,
        profile=active_profile,
        profile_path=profile_path,
        removed=removed,
    )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )
