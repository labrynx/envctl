"""Rebind command."""

from __future__ import annotations

import typer

from envctl.adapters.input import confirm
from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_project_rebind_result
from envctl.cli.prompts import build_project_rebind_confirmation_message
from envctl.services.rebind_service import run_rebind
from envctl.utils.output import print_cancelled


@handle_errors
@requires_writable_runtime("project rebind")
@text_output_only("project rebind")
def project_rebind_command(
    copy_values: bool = typer.Option(
        True,
        "--copy-values/--empty",
        help="Copy current vault values into the new vault, or start empty.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Skip confirmation.",
    ),
) -> None:
    """Rebind the current checkout to a fresh project identity."""
    if not yes:
        approved = confirm(
            message=build_project_rebind_confirmation_message(),
            default=False,
        )
        if not approved:
            print_cancelled()
            return

    context, result = run_rebind(copy_values=copy_values)

    render_project_rebind_result(
        display_name=context.display_name,
        previous_project_id=result.previous_project_id,
        new_project_id=result.new_project_id,
        copied_values=result.copied_values,
        repo_root=context.repo_root,
        vault_dir=context.vault_project_dir,
        vault_values_path=context.vault_values_path,
    )
