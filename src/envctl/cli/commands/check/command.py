"""Check command."""

from __future__ import annotations

import typer

from envctl.cli.command_support import (
    build_json_command_payload,
    render_contract_warnings_if_any,
)
from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_check_result
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.cli.serializers import emit_json, serialize_check_result
from envctl.services.check_service import run_check


@handle_errors
def check_command() -> None:
    """Validate the current project environment against the contract."""
    context, result, warnings = run_check(
        get_active_profile(),
        selection=get_contract_selection(),
    )

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="check",
                ok=result.ok,
                data=serialize_check_result(result, context=context),
                contract_warnings=warnings,
                command_warnings=result.warnings,
            )
        )
        if not result.ok:
            raise typer.Exit(code=1)
        return

    render_contract_warnings_if_any(warnings)
    render_check_result(result)

    if not result.ok:
        raise typer.Exit(code=1)
