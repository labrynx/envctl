"""Inspect command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import (
    render_contract_deprecation_warnings,
    render_resolution_view,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_contract_deprecation_warnings,
    serialize_contract_selection,
    serialize_project_context,
    serialize_resolution_report,
)
from envctl.services.inspect_service import run_inspect


@handle_errors
def inspect_command() -> None:
    """Inspect the resolved environment."""
    selection = get_contract_selection()
    context, active_profile, report, warnings = run_inspect(
        get_active_profile(),
        selection=selection,
    )

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "inspect",
                "data": {
                    "active_profile": active_profile,
                    "selection": serialize_contract_selection(selection),
                    "warnings": serialize_contract_deprecation_warnings(warnings),
                    "context": serialize_project_context(context),
                    "report": serialize_resolution_report(report),
                },
            }
        )
        return

    if warnings:
        render_contract_deprecation_warnings(warnings)

    render_resolution_view(
        profile=active_profile,
        selection=selection,
        report=report,
    )
