"""Vault edit command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.services.vault_service import run_vault_edit
from envctl.utils.output import print_kv, print_success


@handle_errors
@requires_writable_runtime("vault edit")
@text_output_only("vault edit")
def vault_edit_command() -> None:
    """Open the local vault file in the configured editor."""
    _context, result = run_vault_edit()

    if result.created:
        print_success("Created and opened local vault file")
    else:
        print_success("Opened local vault file")

    print_kv("vault_values", str(result.path))