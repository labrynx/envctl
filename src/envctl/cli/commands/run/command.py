"""Run command."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters.deprecation_presenter import (
    render_contract_deprecation_warnings,
)
from envctl.cli.presenters.run_presenter import render_run_warnings
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.errors import ExecutionError
from envctl.services.run_service import run_command

COMMAND_ARGUMENT = typer.Argument(...)


@handle_errors
def run_command_cli(command: list[str] = COMMAND_ARGUMENT) -> None:
    """Run a child process with the resolved environment injected."""
    active_profile = get_active_profile()
    selection = get_contract_selection()

    if is_json_output():
        raise ExecutionError("JSON output is not supported for 'run' yet.")

    _context, result, warnings = run_command(
        command,
        active_profile,
        selection=selection,
    )

    render_contract_deprecation_warnings(cast(Sequence[ContractDeprecationWarning], warnings))
    render_run_warnings(result.warnings)
    raise typer.Exit(code=result.exit_code)
