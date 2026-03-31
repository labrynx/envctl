"""Profile copy command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters import render_profile_copy_result
from envctl.services.profile_service import run_profile_copy

SOURCE_ARGUMENT = typer.Argument(...)
TARGET_ARGUMENT = typer.Argument(...)


@handle_errors
@requires_writable_runtime("profile copy")
@text_output_only("profile copy")
def profile_copy_command(
    source: str = SOURCE_ARGUMENT,
    target: str = TARGET_ARGUMENT,
) -> None:
    """Copy one profile into another."""
    _context, result = run_profile_copy(source, target)

    render_profile_copy_result(
        source_profile=result.source_profile,
        target_profile=result.target_profile,
        source_path=result.source_path,
        target_path=result.target_path,
        copied_keys=result.copied_keys,
    )
