"""Inspect command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import (
    render_contract_deprecation_warnings,
    render_inspect_key_result,
    render_inspect_result,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_command_warnings,
    serialize_contract_deprecation_warnings,
    serialize_inspect_key_result,
    serialize_inspect_result,
)
from envctl.errors import ExecutionError
from envctl.services.inspect_service import run_inspect, run_inspect_key


@handle_errors
def inspect_command(key: str | None = typer.Argument(None)) -> None:
    """Inspect the resolved environment or one key in detail."""
    if key is not None:
        selection = get_contract_selection()
        if selection.mode != "full":
            raise ExecutionError(
                "Cannot combine `inspect KEY` with --group, --set, or --var. "
                "Use either a positional key or a scope selector."
            )
        _context, key_result, warnings = run_inspect_key(key, get_active_profile())

        if is_json_output():
            emit_json(
                {
                    "ok": True,
                    "command": "inspect",
                    "data": {
                        **serialize_inspect_key_result(key_result),
                        "warnings": serialize_contract_deprecation_warnings(warnings)
                        + serialize_command_warnings(key_result.warnings),
                    },
                }
            )
            return

        if warnings:
            render_contract_deprecation_warnings(warnings)
        render_inspect_key_result(key_result)
        return

    _context, inspect_result, warnings = run_inspect(
        get_active_profile(),
        selection=get_contract_selection(),
    )

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "inspect",
                "data": {
                    **serialize_inspect_result(inspect_result),
                    "warnings": serialize_contract_deprecation_warnings(warnings)
                    + serialize_command_warnings(inspect_result.warnings),
                },
            }
        )
        return

    if warnings:
        render_contract_deprecation_warnings(warnings)

    render_inspect_result(inspect_result)
