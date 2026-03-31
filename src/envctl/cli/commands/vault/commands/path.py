"""Vault path command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_vault_path_result
from envctl.cli.runtime import get_active_profile
from envctl.services.vault_service import run_vault_path


@handle_errors
@text_output_only("vault path")
def vault_path_command() -> None:
    """Print the current vault file path."""
    _context, active_profile, path = run_vault_path(get_active_profile())

    render_vault_path_result(
        profile=active_profile,
        path=path,
    )
