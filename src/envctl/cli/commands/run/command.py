"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters.run_presenter import render_run_warnings
from envctl.cli.runtime import get_active_profile, get_selected_group, is_json_output
from envctl.errors import ExecutionError
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(...)


@handle_errors
def run_command_cli(command: list[str] = COMMAND_ARGUMENT) -> None:
    """Run a child process with the resolved environment injected."""
    active_profile = get_active_profile()
    selected_group = get_selected_group()

    if is_json_output():
        raise ExecutionError("JSON output is not supported for 'run' yet.")

    _context, result = run_command(
        command,
        active_profile,
        group=selected_group,
    )
    render_run_warnings(result.warnings)
    raise typer.Exit(code=result.exit_code)
