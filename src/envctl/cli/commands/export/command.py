"""Export command."""

from __future__ import annotations

from typing import Literal

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.actions import build_export_output
from envctl.cli.presenters.outputs.warnings import (
    build_contract_deprecation_warnings_output,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output

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
def export_command(
    format: ExportFormat = FORMAT_OPTION,
) -> None:
    """Print the resolved environment as shell export lines."""
    from envctl.services.export_service import run_export

    _context, resolved_profile, values, rendered, warnings = run_export(
        get_active_profile(),
        format=format,
        selection=get_contract_selection(),
    )

    if not is_json_output() and format == "dotenv":
        print(rendered, end="")
        return

    output = build_export_output(
        active_profile=resolved_profile,
        format=format,
        values=values,
        rendered=rendered,
    )

    if warnings:
        output = merge_outputs(
            build_contract_deprecation_warnings_output(warnings, stderr=not is_json_output()),
            output,
        )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )
