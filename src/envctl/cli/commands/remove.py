"""Remove command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_remove_result
from envctl.services.remove_service import run_remove


@handle_errors
def remove_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Remove envctl management for the current repository."""
    result = run_remove(force=yes, confirm=typer_confirm)
    render_remove_result(result)
