"""Inspect command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_resolution
from envctl.cli.runtime import is_json_output
from envctl.cli.serializers import emit_json, serialize_project_context, serialize_resolution_report
from envctl.services.inspect_service import run_inspect


@handle_errors
def inspect_command() -> None:
    """Inspect the resolved environment."""
    context, report = run_inspect()

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "inspect",
                "data": {
                    "context": serialize_project_context(context),
                    "report": serialize_resolution_report(report),
                },
            }
        )
        return

    render_resolution(report)