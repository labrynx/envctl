"""Repair command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_project_repair_result
from envctl.services.repair_service import run_repair


@handle_errors
@requires_writable_runtime("project repair")
@text_output_only("project repair")
def project_repair_command(
    create_if_missing: bool = typer.Option(
        False,
        "--create-if-missing",
        help="Create and persist a new binding when no persisted identity exists yet.",
    ),
    recreate_bound_vault: bool = typer.Option(
        False,
        "--recreate-bound-vault",
        help="Recreate the missing vault for the current bound project id.",
    ),
) -> None:
    """Repair a missing, recovered, or incomplete local binding."""
    context, result = run_repair(
        create_if_missing=create_if_missing,
        recreate_bound_vault=recreate_bound_vault,
    )

    render_project_repair_result(
        status=result.status,
        detail=result.detail,
        project_id=context.project_id if context is not None else result.project_id,
        binding_source=context.binding_source if context is not None else None,
        repo_root=context.repo_root if context is not None else None,
        vault_dir=context.vault_project_dir if context is not None else None,
        vault_values_path=context.vault_values_path if context is not None else None,
    )
