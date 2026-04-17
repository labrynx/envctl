"""Status command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.status import build_status_view_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
def status_command() -> None:
    """Show a human-oriented project status summary."""
    from envctl.services.status_service import run_status

    active_profile, report = run_status(get_active_profile())

    present(
        build_status_view_output(
            profile=active_profile,
            report=report,
        ),
        output_format="json" if is_json_output() else "text",
    )
