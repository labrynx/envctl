"""Vault path command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.runtime import get_active_profile
from envctl.services.vault_service import run_vault_path
from envctl.utils.output import print_kv


@handle_errors
@text_output_only("vault path")
def vault_path_command() -> None:
    """Print the current vault file path."""
    _context, active_profile, path = run_vault_path(get_active_profile())
    print_kv("profile", active_profile)
    print_kv("vault_values", str(path))
