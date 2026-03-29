"""Vault edit command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.services.edit_service import run_vault_edit
from envctl.utils.output import print_kv, print_success


@handle_errors
def vault_edit_command() -> None:
    """Open the local vault file in the configured editor."""
    _context, result = run_vault_edit()

    if result.created:
        print_success("Created and opened local vault file")
    else:
        print_success("Opened local vault file")

    print_kv("vault_values", str(result.path))
