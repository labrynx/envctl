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
    from envctl.domain.vault import summarize_vault_audit
    from envctl.services.vault_service import run_vault_audit

    _context, projects = run_vault_audit()
    summary = summarize_vault_audit(projects)

    present(
        build_vault_audit_output(projects, summary=summary),
        output_format="json" if is_json_output() else "text",
    )

    if not summary.ok:
        raise typer.Exit(code=1)
