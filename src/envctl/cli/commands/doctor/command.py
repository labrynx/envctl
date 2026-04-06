"""Doctor command."""

from __future__ import annotations

from typing import Any

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_contract_deprecation_warnings, render_inspect_result
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_command_warnings,
    serialize_contract_deprecation_warnings,
    serialize_inspect_result,
)
from envctl.domain.diagnostics import CommandWarning, InspectResult
from envctl.services.doctor_service import run_doctor


def _serialize_legacy_checks(result: InspectResult) -> dict[str, Any]:
    checks = [
        {
            "name": "project",
            "status": "ok",
            "detail": f"Resolved project: {result.project.display_name}",
        },
        {
            "name": "active_profile",
            "status": "ok",
            "detail": f"Active profile: {result.active_profile}",
        },
    ]
    return {
        "has_failures": False,
        "checks": checks,
    }


@handle_errors
def doctor_command() -> None:
    """Deprecated alias for ``inspect``."""
    _context, result, warnings = run_doctor(get_active_profile())
    alias_warning = CommandWarning(
        kind="deprecated_command",
        message=(
            "Warning: `envctl doctor` is deprecated and will be removed in v2.6.0.\n"
            "Use `envctl inspect` instead."
        ),
    )

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "doctor",
                "data": {
                    **serialize_inspect_result(result),
                    **_serialize_legacy_checks(result),
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
    render_inspect_result(result)
