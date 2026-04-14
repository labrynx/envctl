"""Vault audit command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters.vault_presenter import render_vault_audit_result


@handle_errors
@text_output_only("vault audit")
def vault_audit_command() -> None:
    """Audit every persisted vault project for plaintext or inconsistent files."""
    from envctl.services.vault_service import run_vault_audit

    _context, projects = run_vault_audit()
    render_vault_audit_result(projects)

    has_issues = any(
        (not project.key_exists)
        or any(
            (item.state != "encrypted") or (not item.private_permissions) for item in project.files
        )
        for project in projects
    )
    if has_issues:
        raise typer.Exit(code=1)
