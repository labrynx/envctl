"""Status command."""

from __future__ import annotations

from envctl.cli.command_support import build_json_command_payload
from envctl.cli.decorators import handle_errors
from envctl.cli.presenters.status_presenter import render_status_view
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers.common import emit_json
from envctl.cli.serializers.status import serialize_status_report


@handle_errors
def status_command() -> None:
    """Show a human-oriented project status summary."""
    from envctl.services.status_service import run_status

    active_profile, report = run_status(get_active_profile())

    if is_json_output():
        payload = serialize_status_report(report)
        payload["active_profile"] = active_profile
        emit_json(
            build_json_command_payload(
                command="status",
                data=payload,
            )
        )
        return

    render_status_view(
        profile=active_profile,
        report=report,
    )
