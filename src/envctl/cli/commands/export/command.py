"""Export command."""

from __future__ import annotations

from typing import Literal

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_export_output
from envctl.cli.runtime import get_active_profile, get_selected_group, is_json_output
from envctl.errors import ExecutionError
from envctl.services.export_service import run_export


@handle_errors
def export_command(
    format: Literal["shell", "dotenv"] = typer.Option(
        "shell",
        "--format",
        help=(
            "Choose the export format: 'shell' prints shell export lines, "
            "'dotenv' prints KEY=value lines to stdout."
        ),
    ),
) -> None:
    """Print the resolved environment as shell export lines."""
    active_profile = get_active_profile()
    selected_group = get_selected_group()

    if is_json_output():
        raise ExecutionError("JSON output is not supported for 'export' yet.")

    _context, resolved_profile, rendered = run_export(
        active_profile,
        format=format,
        group=selected_group,
    )

    if format == "dotenv":
        print(rendered, end="")
        return

    render_export_output(profile=resolved_profile, rendered=rendered)
