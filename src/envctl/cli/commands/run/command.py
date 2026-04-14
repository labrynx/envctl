"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.command_support import render_contract_warnings_if_any
from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters.run_presenter import render_run_warnings
from envctl.cli.runtime import get_active_profile, get_contract_selection

COMMAND_ARGUMENT = typer.Argument(...)


@handle_errors
@text_output_only("run")
def run_command_cli(command: list[str] = COMMAND_ARGUMENT) -> None:
    """Run a child process with the resolved environment injected."""
    from envctl.services.run_service import run_command

    _context, result, warnings = run_command(
        command,
        get_active_profile(),
        selection=get_contract_selection(),
    )

    render_contract_warnings_if_any(warnings)
    render_run_warnings(result.warnings)
    raise typer.Exit(code=result.exit_code)
