"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(..., metavar="COMMAND [ARGS]...")


@handle_errors
@text_output_only("run")
def run_command_cli(
    command: list[str] = COMMAND_ARGUMENT,
) -> None:
    """Run a command with the resolved environment injected."""
    raise typer.Exit(code=run_command(command))