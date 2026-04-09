"""Presenters for structured state errors."""

from __future__ import annotations

from envctl.cli.presenters.common import (
    print_action_list,
    print_error_title,
    print_kv_line,
    print_section,
)
from envctl.domain.error_diagnostics import StateDiagnostics


def render_state_error(
    diagnostics: StateDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured state error to stderr."""
    print_error_title(message)
    print_section("Context", err=True)
    print_kv_line("path", str(diagnostics.path), err=True)
    if diagnostics.field is not None:
        print_kv_line("field", diagnostics.field, err=True)

    print_action_list(diagnostics.suggested_actions, err=True)
