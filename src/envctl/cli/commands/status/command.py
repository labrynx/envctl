"""Status command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.formatters import render_status
from envctl.cli.runtime import is_json_output
from envctl.cli.serializers import emit_json, serialize_status_report
from envctl.services.status_service import run_status


@handle_errors
def status_command() -> None:
    """Show the current project status."""
    report = run_status()

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "status",
                "data": serialize_status_report(report),
            }
        )
        return

    render_status(report)
