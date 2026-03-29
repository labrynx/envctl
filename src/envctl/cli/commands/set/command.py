"""Set command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.set_service import run_set
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def set_command(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
) -> None:
    """Create or update one key in the local vault only."""
    context, result = run_set(key=key, value=value)

    print_success(f"Updated '{key}' in local vault")
    print_kv("vault_values", str(context.vault_values_path))

    if not result.declared_in_contract:
        print_warning("Key is not declared in the contract.")
