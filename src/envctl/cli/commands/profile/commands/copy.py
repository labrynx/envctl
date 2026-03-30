"""Profile copy command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.services.profile_service import run_profile_copy
from envctl.utils.output import print_kv, print_success

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

    print_success(f"Copied profile '{result.source_profile}' into '{result.target_profile}'")
    print_kv("source_profile", result.source_profile)
    print_kv("target_profile", result.target_profile)
    print_kv("source_path", str(result.source_path))
    print_kv("target_path", str(result.target_path))
    print_kv("copied_keys", str(result.copied_keys))
