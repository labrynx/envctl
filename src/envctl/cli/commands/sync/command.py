"""Sync command."""

from __future__ import annotations

from pathlib import Path

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.actions import build_sync_output
from envctl.cli.presenters.outputs.warnings import (
    build_contract_deprecation_warnings_output,
)
from envctl.cli.runtime import (
    get_active_profile,
    get_contract_selection,
    is_json_output,
)

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
    from envctl.services.sync_service import run_sync

    _context, active_profile, target_path, warnings = run_sync(
        get_active_profile(),
        output_path=output_path,
        selection=get_contract_selection(),
    )

    output = merge_outputs(
        build_contract_deprecation_warnings_output(warnings, stderr=not is_json_output()),
        build_sync_output(
            profile=active_profile,
            target_path=target_path,
        ),
    )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )
