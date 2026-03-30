"""Doctor command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_doctor_checks
from envctl.cli.runtime import is_json_output
from envctl.cli.serializers import emit_json, serialize_doctor_checks
from envctl.services.doctor_service import run_doctor


@handle_errors
def doctor_command() -> None:
    """Run local read-only diagnostics."""
    checks = run_doctor()

    if is_json_output():
        data = serialize_doctor_checks(checks)
        emit_json(
            {
                "ok": not data["has_failures"],
                "command": "doctor",
                "data": data,
            }
        )
        if data["has_failures"]:
            raise typer.Exit(code=1)
        return

    has_failures = render_doctor_checks(checks)
    if has_failures:
        raise typer.Exit(code=1)
