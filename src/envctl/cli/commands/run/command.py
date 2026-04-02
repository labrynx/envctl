"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters.run_presenter import render_run_warnings
from envctl.cli.runtime import get_active_profile
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(...)


@handle_errors
@text_output_only("run")
def run_command_cli(command: list[str] = COMMAND_ARGUMENT) -> None:
    """Run a child process with the resolved environment injected."""
    _context, result = run_command(
        command,
        get_active_profile(),
    )
    render_run_warnings(result.warnings)
    raise typer.Exit(code=result.exit_code)
