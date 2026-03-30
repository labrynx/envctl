"""Remove command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.runtime import get_active_profile
from envctl.domain.operations import RemovePlan
from envctl.services.remove_service import plan_remove, run_remove
from envctl.utils.output import print_kv, print_success, print_warning

KEY_ARGUMENT = typer.Argument(...)
YES_OPTION = typer.Option(False, "--yes", help="Skip confirmation.")


def _build_remove_confirmation_message(key: str, plan: RemovePlan) -> str:
    """Build the remove confirmation message."""
    lines = [f"Remove '{key}' from the contract and all profiles?"]

    if plan.present_in_active_profile:
        lines.append("- present in the active profile")

    if plan.present_in_other_profiles:
        lines.append(f"- also present in: {', '.join(plan.present_in_other_profiles)}")

    return "\n".join(lines)


@handle_errors
@requires_writable_runtime("remove")
@text_output_only("remove")
def remove_command(
    key: str = KEY_ARGUMENT,
    yes: bool = YES_OPTION,
) -> None:
    """Remove one key from the contract and all persisted profiles."""
    _context, plan = plan_remove(key, get_active_profile())

    if not yes:
        approved = typer_confirm(
            _build_remove_confirmation_message(key, plan),
            default=False,
        )
        if not approved:
            print_warning("Nothing was changed.")
            return

    context, result = run_remove(key, get_active_profile())

    print_success(f"Removed '{key}' from contract and persisted profiles")
    print_kv("contract", str(result.repo_contract_path))
    print_kv("removed_from_contract", "yes" if result.removed_from_contract else "no")
    print_kv(
        "removed_from_profiles",
        ", ".join(result.removed_from_profiles) if result.removed_from_profiles else "none",
    )
    if result.affected_paths:
        print_kv("affected_paths", ", ".join(str(path) for path in result.affected_paths))
    print_kv("repo_root", str(context.repo_root))
