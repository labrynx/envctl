"""Profile copy command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_profile_copy_output
from envctl.cli.runtime import is_json_output

SOURCE_ARGUMENT = typer.Argument(...)
TARGET_ARGUMENT = typer.Argument(...)


@handle_errors
@requires_writable_runtime("profile copy")
def profile_copy_command(
    source: str = SOURCE_ARGUMENT,
    target: str = TARGET_ARGUMENT,
) -> None:
    """Copy one profile into another."""
    from envctl.services.profile_service import run_profile_copy

    _context, result = run_profile_copy(source, target)

    present(
        build_profile_copy_output(
            source_profile=result.source_profile,
            target_profile=result.target_profile,
            source_path=result.source_path,
            target_path=result.target_path,
            copied_keys=result.copied_keys,
        ),
        output_format="json" if is_json_output() else "text",
    )
