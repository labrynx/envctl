"""Vault prune command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors
from envctl.services.vault_service import get_unknown_vault_keys, run_vault_prune
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def vault_prune_command(
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Skip confirmation.",
    ),
) -> None:
    """Remove vault keys that are not declared in the contract."""
    context, unknown_keys = get_unknown_vault_keys()
    print_kv("vault_values", str(context.vault_values_path))

    if not unknown_keys:
        print_warning("No unknown keys were removed")
        return

    if not yes:
        approved = typer_confirm(
            f"Remove {len(unknown_keys)} unknown key(s) from the local vault?",
            False,
        )
        if not approved:
            print_warning("No unknown keys were removed")
            print_kv("kept_keys", "unchanged")
            return

    _context, result = run_vault_prune()

    print_success(f"Removed {len(result.removed_keys)} unknown key(s) from local vault")
    print_kv("removed_keys", ", ".join(result.removed_keys))
    print_kv("kept_keys", str(result.kept_keys))
