"""Vault decrypt command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_vault_decrypt_result
from envctl.services.vault_service import run_vault_decrypt_project

ALL_OPTION = typer.Option(
    False,
    "--all",
    help="Decrypt vault files for every persisted project, not just the active one.",
)


@handle_errors
@requires_writable_runtime("vault decrypt")
@text_output_only("vault decrypt")
def vault_decrypt_command(
    all_projects: bool = ALL_OPTION,
) -> None:
    """Decrypt encrypted vault files for the current project or all projects."""
    _context, result = run_vault_decrypt_project(include_all_projects=all_projects)
    render_vault_decrypt_result(result)
