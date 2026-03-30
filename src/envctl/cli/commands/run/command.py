"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(..., metavar="COMMAND [ARGS]...")


@handle_errors
def run_command(
    command: list[str] = COMMAND_ARGUMENT,
) -> None:
    """Run a command with the resolved environment injected."""
    raise typer.Exit(code=run_command(command))
