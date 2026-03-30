"""Inspect command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_resolution
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json, serialize_project_context, serialize_resolution_report
from envctl.services.inspect_service import run_inspect
from envctl.utils.output import print_kv


@handle_errors
def inspect_command() -> None:
    """Inspect the resolved environment."""
    context, active_profile, report = run_inspect(get_active_profile())

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "inspect",
                "data": {
                    "active_profile": active_profile,
                    "context": serialize_project_context(context),
                    "report": serialize_resolution_report(report),
                },
            }
        )
        return

    print_kv("profile", active_profile)
    typer.echo()
    render_resolution(report)
