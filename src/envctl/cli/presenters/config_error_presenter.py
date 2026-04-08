"""Presenters for structured configuration errors."""

from __future__ import annotations

from envctl.cli.presenters.common import (
    print_action_list,
    print_error_title,
    print_kv_line,
    print_section,
)
from envctl.domain.error_diagnostics import ConfigDiagnostics


def render_config_error(
    diagnostics: ConfigDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured config error to stderr."""
    print_error_title(message)

    has_details = any(
        value is not None
        for value in (
            diagnostics.path,
            diagnostics.source_label,
            diagnostics.key,
            diagnostics.field,
            diagnostics.value,
        )
    )
    if has_details:
        print_section("Context", err=True)

    if diagnostics.path is not None:
        print_kv_line("path", str(diagnostics.path), err=True)
    if diagnostics.source_label is not None:
        print_kv_line("source", diagnostics.source_label, err=True)
    if diagnostics.key is not None:
        print_kv_line("key", diagnostics.key, err=True)
    if diagnostics.field is not None:
        print_kv_line("field", diagnostics.field, err=True)
    if diagnostics.value is not None:
        print_kv_line("value", diagnostics.value, err=True)

    print_action_list(diagnostics.suggested_actions, err=True)
