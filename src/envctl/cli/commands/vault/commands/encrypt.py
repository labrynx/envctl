"""Vault encrypt command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters.vault_presenter import render_vault_encrypt_result

ALL_OPTION = typer.Option(
    False,
    "--all",
    help="Encrypt vault files for every persisted project, not just the active one.",
)


@handle_errors
@requires_writable_runtime("vault encrypt")
@text_output_only("vault encrypt")
def vault_encrypt_command(
    all_projects: bool = ALL_OPTION,
) -> None:
    """Encrypt plaintext vault files for the current project or all projects."""
    from envctl.services.vault_service import run_vault_encrypt_project

    _context, result = run_vault_encrypt_project(include_all_projects=all_projects)
    render_vault_encrypt_result(result)
