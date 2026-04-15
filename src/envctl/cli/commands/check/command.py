"""Check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.outputs.status import build_check_output
from envctl.cli.presenters.outputs.warnings import (
    build_command_warnings_output,
    build_contract_deprecation_warnings_output,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output


@handle_errors
def check_command() -> None:
    """Validate the current project environment against the contract."""
    from envctl.services.check_service import run_check

    context, result, warnings = run_check(
        get_active_profile(),
        selection=get_contract_selection(),
    )

    output = merge_outputs(
        build_contract_deprecation_warnings_output(warnings),
        build_command_warnings_output(result.warnings),
        build_check_output(result, context=context),
    )

    present(
        output,
        output_format="json" if is_json_output() else "text",
    )

    if not result.ok:
        raise typer.Exit(code=1)
