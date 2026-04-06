"""Sync command."""

from __future__ import annotations

from pathlib import Path

import typer

from envctl.cli.command_support import render_contract_warnings_if_any
from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import render_sync_result
from envctl.cli.runtime import get_active_profile, get_contract_selection
from envctl.services.sync_service import run_sync

SYNC_OUTPUT_PATH_OPTION = typer.Option(
    None,
    "--output-path",
    help="Custom output path.",
)


@handle_errors
@requires_writable_runtime("sync")
def sync_command(
    output_path: Path | None = SYNC_OUTPUT_PATH_OPTION,
) -> None:
    """Write the resolved environment into a repository env file."""
    _context, active_profile, target_path, warnings = run_sync(
        get_active_profile(),
        output_path=output_path,
        selection=get_contract_selection(),
    )

    render_contract_warnings_if_any(warnings, stderr=True)
    render_sync_result(
        profile=active_profile,
        target_path=target_path,
    )
