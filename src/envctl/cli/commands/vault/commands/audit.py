"""Vault audit command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import build_vault_audit_output
from envctl.cli.runtime import is_json_output


@handle_errors
def vault_audit_command() -> None:
    """Audit every persisted vault project for plaintext or inconsistent files."""
    from envctl.services.vault_service import run_vault_audit

    _context, projects = run_vault_audit()

    present(
        build_vault_audit_output(projects),
        output_format="json" if is_json_output() else "text",
    )

    has_issues = any(
        (not project.key_exists)
        or any(
            (item.state != "encrypted") or (not item.private_permissions) for item in project.files
        )
        for project in projects
    )
    if has_issues:
        raise typer.Exit(code=1)
