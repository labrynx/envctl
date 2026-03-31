"""Status command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_status_view
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json, serialize_status_report
from envctl.services.status_service import run_status


@handle_errors
def status_command() -> None:
    """Show a human-oriented project status summary."""
    active_profile, report = run_status(get_active_profile())

    if is_json_output():
        payload = serialize_status_report(report)
        payload["active_profile"] = active_profile
        emit_json(
            {
                "ok": True,
                "command": "status",
                "data": payload,
            }
        )
        return

    render_status_view(
        profile=active_profile,
        report=report,
    )
