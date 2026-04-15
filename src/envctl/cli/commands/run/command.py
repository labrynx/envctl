"""Run command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.actions import build_run_warnings_output
from envctl.cli.presenters.outputs.warnings import (
    build_contract_deprecation_warnings_output,
)
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

    output = merge_outputs(
        build_contract_deprecation_warnings_output(warnings),
        build_run_warnings_output(result.warnings),
    )

    present(output, output_format="text")
    raise typer.Exit(code=result.exit_code)
