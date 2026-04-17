"""Set command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_set_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
@requires_writable_runtime("set")
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

    present(
        build_set_output(
            key=key,
            profile=active_profile,
            profile_path=profile_path,
        ),
        output_format="json" if is_json_output() else "text",
    )
