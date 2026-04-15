"""Vault edit command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import build_vault_edit_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
@requires_writable_runtime("vault edit")
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

    from envctl.services.vault_service import run_vault_edit

    _context, result = run_vault_edit(selected_profile)

    present(
        build_vault_edit_output(
            profile=result.profile,
            path=result.path,
            created=result.created,
        ),
        output_format="json" if is_json_output() else "text",
    )
