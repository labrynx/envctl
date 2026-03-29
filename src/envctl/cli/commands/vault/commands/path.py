"""Vault path command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.services.vault_service import run_vault_path
from envctl.utils.output import print_kv


@handle_errors
def vault_path_command() -> None:
    """Print the current vault file path."""
    _context, path = run_vault_path()
    print_kv("vault_values", path)
