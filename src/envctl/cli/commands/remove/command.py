"""Remove command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters.action_presenter import render_remove_result
from envctl.cli.prompts.confirmation_prompts import build_remove_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import get_active_profile
from envctl.utils.output import print_cancelled

KEY_ARGUMENT = typer.Argument(...)
YES_OPTION = typer.Option(False, "--yes", help="Skip confirmation.")


@handle_errors
@requires_writable_runtime("remove")
@text_output_only("remove")
def remove_command(
    key: str = KEY_ARGUMENT,
    yes: bool = YES_OPTION,
) -> None:
    """Remove one key from the contract and all persisted profiles."""
    from envctl.services.remove_service import plan_remove, run_remove

    _context, plan = plan_remove(key, get_active_profile())

    if not yes:
        approved = confirm(
            build_remove_confirmation_message(
                key,
                present_in_active_profile=plan.present_in_active_profile,
                present_in_other_profiles=plan.present_in_other_profiles,
                absent_in_other_profiles=plan.absent_in_other_profiles,
            ),
            default=False,
        )
        if not approved:
            print_cancelled()
            return

    context, result = run_remove(key, get_active_profile())

    render_remove_result(
        key=key,
        contract_path=result.repo_contract_path,
        removed_from_contract=result.removed_from_contract,
        inspected_profiles=result.inspected_profiles,
        removed_from_profiles=result.removed_from_profiles,
        missing_from_profiles=result.missing_from_profiles,
        affected_paths=result.affected_paths,
        repo_root=context.repo_root,
    )
