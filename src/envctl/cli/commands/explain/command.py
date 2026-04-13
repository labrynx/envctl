"""Explain command."""

from __future__ import annotations

import typer

from envctl.cli.command_support import (
    build_json_command_payload,
    render_contract_warnings_if_any,
)
from envctl.cli.compat.deprecated_commands import build_deprecated_command_warning
from envctl.cli.decorators import handle_errors
from envctl.cli.presenters.inspect_presenter import render_inspect_key_result
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers.common import emit_json
from envctl.cli.serializers.inspect import serialize_inspect_key_result


@handle_errors
def explain_command(key: str = typer.Argument(...)) -> None:
    """Deprecated alias for ``inspect KEY``."""
    from envctl.services.inspect_service import run_inspect_key

    _context, result, warnings = run_inspect_key(key, get_active_profile())
    alias_warning = build_deprecated_command_warning(
        command_name="envctl explain",
        replacement="envctl inspect KEY",
        removal_version="v2.6.0",
    )

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="explain",
                data=serialize_inspect_key_result(result),
                contract_warnings=warnings,
                command_warnings=result.warnings,
                extra_warnings=(alias_warning,),
            )
        )
        return

    render_contract_warnings_if_any(warnings)
    typer.echo(alias_warning.message)
    typer.echo()
    render_inspect_key_result(result)
