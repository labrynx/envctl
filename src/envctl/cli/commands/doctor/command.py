"""Doctor command."""

from __future__ import annotations

from typing import Any

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_doctor_checks
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json
from envctl.services.doctor_service import run_doctor


def _build_doctor_json_payload(
    active_profile: str,
    checks: list[Any],
) -> dict[str, object]:
    """Build the JSON payload for doctor output."""
    has_failures = any(check.status == "fail" for check in checks)
    return {
        "ok": not has_failures,
        "command": "doctor",
        "data": {
            "active_profile": active_profile,
            "has_failures": has_failures,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "detail": check.detail,
                }
                for check in checks
            ],
        },
    }


@handle_errors
def doctor_command() -> None:
    """Run read-only diagnostics for envctl."""
    active_profile, checks = run_doctor(get_active_profile())

    if is_json_output():
        payload = _build_doctor_json_payload(active_profile, checks)
        emit_json(payload)
        has_failures = bool(payload["data"]["has_failures"])  # type: ignore[index]
        if has_failures:
            raise typer.Exit(code=1)
        return

    has_failures = render_doctor_checks(checks)
    if has_failures:
        raise typer.Exit(code=1)
