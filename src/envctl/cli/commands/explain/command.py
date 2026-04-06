"""Explain command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import (
    render_contract_deprecation_warnings,
    render_inspect_key_result,
)
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_command_warnings,
    serialize_contract_deprecation_warnings,
    serialize_inspect_key_result,
)
from envctl.domain.diagnostics import CommandWarning
from envctl.services.explain_service import run_explain


@handle_errors
def explain_command(key: str = typer.Argument(...)) -> None:
    """Deprecated alias for ``inspect KEY``."""
    _context, result, warnings = run_explain(key, get_active_profile())
    alias_warning = CommandWarning(
        kind="deprecated_command",
        message=(
            "Warning: `envctl explain` is deprecated and will be removed in v2.6.0.\n"
            "Use `envctl inspect KEY` instead."
        ),
    )

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "explain",
                "data": {
                    **serialize_inspect_key_result(result),
                    "warnings": serialize_contract_deprecation_warnings(warnings)
                    + serialize_command_warnings(result.warnings)
                    + serialize_command_warnings((alias_warning,)),
                },
            }
        )
        return

    render_contract_deprecation_warnings(warnings)
    typer.echo(alias_warning.message)
    typer.echo()
    render_inspect_key_result(result)
