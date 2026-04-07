"""Vault prune command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters import (
    render_vault_prune_cancelled,
    render_vault_prune_no_changes,
    render_vault_prune_result,
)
from envctl.cli.prompts import build_vault_prune_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import get_active_profile
from envctl.services.vault_service import get_unknown_vault_keys, run_vault_prune

YES_OPTION = typer.Option(
    False,
    "--yes",
    help="Skip confirmation.",
)


@handle_errors
@requires_writable_runtime("vault prune")
@text_output_only("vault prune")
def vault_prune_command(
    yes: bool = YES_OPTION,
) -> None:
    """Remove vault keys that are not declared in the contract."""
    _context, active_profile, profile_path, unknown_keys = get_unknown_vault_keys(
        get_active_profile()
    )

    if not unknown_keys:
        render_vault_prune_no_changes(
            profile=active_profile,
            path=profile_path,
        )
        return

    if not yes:
        approved = confirm(
            message=build_vault_prune_confirmation_message(
                profile=active_profile,
                unknown_key_count=len(unknown_keys),
            ),
            default=False,
        )
        if not approved:
            render_vault_prune_cancelled(
                profile=active_profile,
                path=profile_path,
            )
            return

    _context, resolved_profile, profile_path, result = run_vault_prune(get_active_profile())

    render_vault_prune_result(
        profile=resolved_profile,
        path=profile_path,
        removed_keys=result.removed_keys,
        kept_keys=result.kept_keys,
    )
