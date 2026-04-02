"""Export command."""

from __future__ import annotations

from typing import Literal

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_export_output
from envctl.cli.runtime import get_active_profile, get_selected_group
from envctl.services.export_service import run_export


@handle_errors
@text_output_only("export")
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
    _context, active_profile, rendered = run_export(
        get_active_profile(),
        format=format,
        group=get_selected_group(),
    )

    if format == "dotenv":
        print(rendered, end="")
        return

    render_export_output(profile=active_profile, rendered=rendered)
