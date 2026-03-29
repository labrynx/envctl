"""Remove command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors
from envctl.services.remove_service import run_remove
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def remove_command(
    key: str = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Remove one key from the local vault and contract."""
    context, result = run_remove(key=key, yes=yes, confirm=typer_confirm)

    if not result.removed_from_vault and not result.removed_from_contract:
        print_warning("Nothing was removed.")
        return

    print_success(f"Removed '{key}' from contract and local vault")
    print_kv("vault_values", str(context.vault_values_path))
    print_kv("contract", str(context.repo_contract_path))
    print_kv("removed_from_vault", "yes" if result.removed_from_vault else "no")
    print_kv("removed_from_contract", "yes" if result.removed_from_contract else "no")
