"""Rebind command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.common import cancelled_output
from envctl.cli.presenters.outputs.actions import build_project_rebind_output
from envctl.cli.prompts.confirmation_prompts import build_project_rebind_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import is_json_output
from envctl.domain.runtime import OutputFormat


@handle_errors
@requires_writable_runtime("project rebind")
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
    output_format: OutputFormat = OutputFormat.JSON if is_json_output() else OutputFormat.TEXT

    if not yes:
        approved = confirm(
            message=build_project_rebind_confirmation_message(),
            default=False,
        )
        if not approved:
            present(
                cancelled_output(
                    kind="project_rebind",
                    copied_values=copy_values,
                ),
                output_format=output_format,
            )
            return

    from envctl.services.rebind_service import run_rebind

    context, result = run_rebind(copy_values=copy_values)

    present(
        build_project_rebind_output(
            display_name=context.display_name,
            previous_project_id=result.previous_project_id,
            new_project_id=result.new_project_id,
            copied_values=result.copied_values,
            repo_root=context.repo_root,
            vault_dir=context.vault_project_dir,
            vault_values_path=context.vault_values_path,
        ),
        output_format=output_format,
    )
