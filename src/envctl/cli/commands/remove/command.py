"""Remove command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.common import cancelled_output
from envctl.cli.presenters.outputs.actions import build_remove_output
from envctl.cli.presenters.presenter import OutputFormat
from envctl.cli.prompts.confirmation_prompts import build_remove_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import get_active_profile, is_json_output

KEY_ARGUMENT = typer.Argument(...)
YES_OPTION = typer.Option(False, "--yes", help="Skip confirmation.")


@handle_errors
@requires_writable_runtime("remove")
def remove_command(
    key: str = KEY_ARGUMENT,
    yes: bool = YES_OPTION,
) -> None:
    """Remove one key from the contract and all persisted profiles."""
    from envctl.services.remove_service import plan_remove, run_remove

    active_profile = get_active_profile()
    output_format: OutputFormat = "json" if is_json_output() else "text"

    _context, plan = plan_remove(key, active_profile)

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
            present(
                cancelled_output(
                    kind="remove",
                    key=key,
                ),
                output_format=output_format,
            )
            return

    context, result = run_remove(key, active_profile)

    present(
        build_remove_output(
            key=key,
            contract_path=result.repo_contract_path,
            removed_from_contract=result.removed_from_contract,
            inspected_profiles=result.inspected_profiles,
            removed_from_profiles=result.removed_from_profiles,
            missing_from_profiles=result.missing_from_profiles,
            affected_paths=result.affected_paths,
            repo_root=context.repo_root,
        ),
        output_format=output_format,
    )
