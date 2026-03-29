"""Unset command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.unset_service import run_unset
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def unset_command(key: str = typer.Argument(...)) -> None:
    """Remove one key from the local vault only."""
    context, result = run_unset(key)

    if result.removed_from_vault:
        print_success(f"Removed '{key}' from local vault")
    else:
        print_warning("Key not present in local vault")

    print_kv("vault_values", str(context.vault_values_path))

    if result.declared_in_contract:
        print_kv("declared_in_contract", "yes")
