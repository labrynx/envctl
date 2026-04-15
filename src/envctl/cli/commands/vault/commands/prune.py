"""Vault prune command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import (
    build_vault_prune_cancelled_output,
    build_vault_prune_no_changes_output,
    build_vault_prune_output,
)
from envctl.cli.presenters.presenter import OutputFormat
from envctl.cli.prompts.confirmation_prompts import build_vault_prune_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import get_active_profile, is_json_output

YES_OPTION = typer.Option(
    False,
    "--yes",
    help="Skip confirmation.",
)


@handle_errors
@requires_writable_runtime("vault prune")
def vault_prune_command(
    yes: bool = YES_OPTION,
) -> None:
    """Remove vault keys that are not declared in the contract."""
    from envctl.services.vault_service import get_unknown_vault_keys, run_vault_prune

    _context, active_profile, profile_path, unknown_keys = get_unknown_vault_keys(
        get_active_profile()
    )

    output_format: OutputFormat = "json" if is_json_output() else "text"

    if not unknown_keys:
        present(
            build_vault_prune_no_changes_output(
                profile=active_profile,
                path=profile_path,
            ),
            output_format=output_format,
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
            present(
                build_vault_prune_cancelled_output(
                    profile=active_profile,
                    path=profile_path,
                ),
                output_format=output_format,
            )
            return

    _context, resolved_profile, resolved_profile_path, result = run_vault_prune(
        get_active_profile()
    )

    present(
        build_vault_prune_output(
            profile=resolved_profile,
            path=resolved_profile_path,
            removed_keys=result.removed_keys,
            kept_keys=result.kept_keys,
        ),
        output_format=output_format,
    )
