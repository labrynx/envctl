"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.runtime import get_active_profile
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(...)


@handle_errors
@text_output_only("run")
def run_command_cli(command: list[str] = COMMAND_ARGUMENT) -> None:
    """Run a child process with the resolved environment injected."""
    _context, _active_profile, exit_code = run_command(
        command,
        get_active_profile(),
    )
    raise typer.Exit(code=exit_code)
