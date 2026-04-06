"""Export command."""

from __future__ import annotations

from typing import Literal

import typer

from envctl.cli.command_support import render_contract_warnings_if_any
from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_export_output
from envctl.cli.runtime import get_active_profile, get_contract_selection
from envctl.services.export_service import run_export

ExportFormat = Literal["shell", "dotenv"]

FORMAT_OPTION = typer.Option(
    "shell",
    "--format",
    help=(
        "Choose the export format: 'shell' prints shell export lines, "
        "'dotenv' prints KEY=value lines to stdout."
    ),
)


@handle_errors
@text_output_only("export")
def export_command(
    format: ExportFormat = FORMAT_OPTION,
) -> None:
    """Print the resolved environment as shell export lines."""
    _context, resolved_profile, rendered, warnings = run_export(
        get_active_profile(),
        format=format,
        selection=get_contract_selection(),
    )

    render_contract_warnings_if_any(warnings, stderr=True)

    if format == "dotenv":
        print(rendered, end="")
        return

    render_export_output(profile=resolved_profile, rendered=rendered)
