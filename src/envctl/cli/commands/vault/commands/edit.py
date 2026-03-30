"""Vault edit command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.runtime import get_active_profile
from envctl.services.vault_service import run_vault_edit
from envctl.utils.output import print_kv, print_success


@handle_errors
@requires_writable_runtime("vault edit")
@text_output_only("vault edit")
def vault_edit_command(
    profile: str | None = typer.Option(
        None,
        "--profile",
        "-p",
        help="Edit a specific profile without changing the global CLI profile.",
    ),
) -> None:
    """Open the local vault file for the selected profile in the configured editor."""
    selected_profile = profile or get_active_profile()
    _context, result = run_vault_edit(selected_profile)

    if result.created:
        print_success(f"Created and opened profile '{result.profile}' vault file")
    else:
        print_success(f"Opened profile '{result.profile}' vault file")

    print_kv("profile", result.profile)
    print_kv("vault_values", str(result.path))
