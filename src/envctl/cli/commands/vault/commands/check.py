"""Vault check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.edit_service import run_vault_check
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def vault_check_command() -> None:
    """Check the local vault file as a physical artifact."""
    _context, result = run_vault_check()

    if not result.exists:
        print_warning("Vault file does not exist")
        print_kv("vault_values", str(result.path))
        raise typer.Exit(code=1)

    if not result.parseable:
        print_warning("Vault file is not parseable")
        print_kv("vault_values", str(result.path))
        raise typer.Exit(code=1)

    if result.private_permissions:
        print_success("Vault file looks valid")
    else:
        print_warning("Vault file is parseable but permissions are not private enough")

    print_kv("vault_values", str(result.path))
    print_kv("parseable", "yes" if result.parseable else "no")
    print_kv("private_permissions", "yes" if result.private_permissions else "no")
    print_kv("keys", str(result.key_count))

    if not result.private_permissions:
        raise typer.Exit(code=1)
