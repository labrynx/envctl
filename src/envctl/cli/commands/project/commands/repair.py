"""Repair command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_project_repair_output
from envctl.cli.runtime import is_json_output


@handle_errors
@requires_writable_runtime("project repair")
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
    from envctl.services.repair_service import run_repair

    context, result = run_repair(
        create_if_missing=create_if_missing,
        recreate_bound_vault=recreate_bound_vault,
    )

    present(
        build_project_repair_output(
            status=result.status,
            detail=result.detail,
            project_id=context.project_id if context is not None else result.project_id,
            binding_source=context.binding_source if context is not None else None,
            repo_root=context.repo_root if context is not None else None,
            vault_dir=context.vault_project_dir if context is not None else None,
            vault_values_path=context.vault_values_path if context is not None else None,
        ),
        output_format="json" if is_json_output() else "text",
    )
