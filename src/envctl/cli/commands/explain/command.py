"""Explain command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import render_explain_value
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json, serialize_project_context, serialize_resolved_value
from envctl.services.explain_service import run_explain


@handle_errors
def explain_command(key: str = typer.Argument(...)) -> None:
    """Explain one resolved key."""
    context, active_profile, item = run_explain(key, get_active_profile())

    if is_json_output():
        emit_json(
            {
                "ok": True,
                "command": "explain",
                "data": {
                    "active_profile": active_profile,
                    "context": serialize_project_context(context),
                    "item": serialize_resolved_value(item),
                },
            }
        )
        return

    render_explain_value(
        profile=active_profile,
        key=item.key,
        source=item.source,
        raw_value=item.raw_value,
        value=item.value,
        masked=item.masked,
        expansion_status=item.expansion_status,
        expansion_refs=item.expansion_refs,
        expansion_error=item.expansion_error.detail if item.expansion_error is not None else None,
        valid=item.valid,
        detail=item.detail,
    )
