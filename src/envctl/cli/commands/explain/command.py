"""Explain command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.cli.serializers import emit_json, serialize_project_context, serialize_resolved_value
from envctl.services.explain_service import run_explain
from envctl.utils.masking import mask_value
from envctl.utils.output import print_kv


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

    print_kv("profile", active_profile)
    print_kv("key", item.key)
    print_kv("source", item.source)
    print_kv("value", mask_value(item.value) if item.masked else item.value)
    print_kv("valid", "yes" if item.valid else "no")
    if item.detail:
        print_kv("detail", item.detail)
