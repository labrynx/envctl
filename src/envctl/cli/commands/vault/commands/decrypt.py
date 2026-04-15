"""Vault decrypt command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import build_vault_decrypt_output
from envctl.cli.runtime import is_json_output

ALL_OPTION = typer.Option(
    False,
    "--all",
    help="Decrypt vault files for every persisted project, not just the active one.",
)


@handle_errors
@requires_writable_runtime("vault decrypt")
def vault_decrypt_command(
    all_projects: bool = ALL_OPTION,
) -> None:
    """Decrypt encrypted vault files for the current project or all projects."""
    from envctl.services.vault_service import run_vault_decrypt_project

    _context, result = run_vault_decrypt_project(include_all_projects=all_projects)

    present(
        build_vault_decrypt_output(result),
        output_format="json" if is_json_output() else "text",
    )
