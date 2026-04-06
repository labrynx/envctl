"""Export command."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, cast

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_export_output
from envctl.cli.presenters.deprecation_presenter import (
    render_contract_deprecation_warnings,
)
from envctl.cli.runtime import (
    get_active_profile,
    get_contract_selection,
    is_json_output,
)
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.errors import ExecutionError
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
def export_command(
    format: ExportFormat = FORMAT_OPTION,
) -> None:
    """Print the resolved environment as shell export lines."""
    active_profile = get_active_profile()
    selection = get_contract_selection()

    if is_json_output():
        raise ExecutionError("JSON output is not supported for 'export' yet.")

    _context, resolved_profile, rendered, warnings = run_export(
        active_profile,
        format=format,
        selection=selection,
    )

    render_contract_deprecation_warnings(
        cast(Sequence[ContractDeprecationWarning], warnings),
        stderr=True,
    )

    if format == "dotenv":
        print(rendered, end="")
        return

    render_export_output(profile=resolved_profile, rendered=rendered)
