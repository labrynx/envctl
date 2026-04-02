"""Sync command."""

from __future__ import annotations

from pathlib import Path

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import render_sync_result
from envctl.cli.runtime import get_active_profile
from envctl.services.sync_service import run_sync


@handle_errors
@requires_writable_runtime("sync")
def sync_command(
    output: Path | None = typer.Option(
        None,
        "--output",
        help=(
            "Write the generated dotenv file to PATH instead of the default "
            "profile-derived repo-local target."
        ),
    ),
) -> None:
    """Materialize the resolved environment into the repository env file."""
    _context, active_profile, target_path = run_sync(
        get_active_profile(),
        output_path=output,
    )
    render_sync_result(profile=active_profile, target_path=target_path)
