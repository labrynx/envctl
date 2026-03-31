"""Doctor command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_doctor_checks
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json, serialize_doctor_checks
from envctl.services.doctor_service import run_doctor


@handle_errors
def doctor_command() -> None:
    """Run read-only diagnostics for envctl."""
    active_profile, checks = run_doctor(get_active_profile())

    if is_json_output():
        serialized = serialize_doctor_checks(checks)
        emit_json(
            {
                "ok": not serialized["has_failures"],
                "command": "doctor",
                "data": {
                    "active_profile": active_profile,
                    **serialized,
                },
            }
        )
        if serialized["has_failures"]:
            raise typer.Exit(code=1)
        return

    has_failures = render_doctor_checks(checks)
    if has_failures:
        raise typer.Exit(code=1)
