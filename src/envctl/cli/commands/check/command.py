"""Check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_resolution_view
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_project_context,
    serialize_resolution_report,
)
from envctl.services.check_service import run_check
from envctl.utils.output import print_success, print_warning


def _is_check_ok(*, is_valid: bool, unknown_keys: list[str] | tuple[str, ...]) -> bool:
    """Return whether the check result is fully acceptable."""
    return is_valid and not unknown_keys


@handle_errors
def check_command() -> None:
    """Validate the current project environment against the contract."""
    context, active_profile, report = run_check(get_active_profile())
    ok = _is_check_ok(
        is_valid=report.is_valid,
        unknown_keys=report.unknown_keys,
    )

    if is_json_output():
        emit_json(
            {
                "ok": ok,
                "command": "check",
                "data": {
                    "active_profile": active_profile,
                    "context": serialize_project_context(context),
                    "report": serialize_resolution_report(report),
                },
            }
        )
        if not ok:
            raise typer.Exit(code=1)
        return

    render_resolution_view(
        profile=active_profile,
        report=report,
    )

    if ok:
        print_success("Environment contract satisfied")
        return

    if report.is_valid:
        print_warning("Environment is valid, but the vault contains unknown keys")
        raise typer.Exit(code=1)

    print_warning("Environment contract is not satisfied")
    raise typer.Exit(code=1)
