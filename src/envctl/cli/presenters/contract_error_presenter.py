"""Presenters for structured contract errors."""

from __future__ import annotations

from envctl.cli.presenters.common import (
    print_action_list,
    print_error_title,
    print_kv_line,
    print_section,
)
from envctl.domain.error_diagnostics import ContractDiagnostics


def render_contract_error(
    diagnostics: ContractDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured contract error to stderr."""
    print_error_title(message)
    print_section("Context", err=True)
    print_kv_line("path", str(diagnostics.path), err=True)
    if diagnostics.field is not None:
        print_kv_line("field", diagnostics.field, err=True)
    if diagnostics.key is not None:
        print_kv_line("key", diagnostics.key, err=True)

    if diagnostics.issues:
        print_section("Contract issues", err=True)
        for issue in diagnostics.issues:
            print_kv_line(issue.field, issue.detail, err=True)

    print_action_list(diagnostics.suggested_actions, err=True)
