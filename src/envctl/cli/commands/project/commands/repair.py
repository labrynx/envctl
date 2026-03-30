"""Repair command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.repair_service import run_repair
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
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

    if result.status in {"healthy", "repaired", "created", "recreated"}:
        print_success(result.detail)
    else:
        print_warning(result.detail)

    if context is not None:
        print_kv("project_id", context.project_id)
        print_kv("binding_source", context.binding_source)
        print_kv("repo_root", str(context.repo_root))
        print_kv("vault_dir", str(context.vault_project_dir))
        print_kv("vault_values", str(context.vault_values_path))
    elif result.project_id is not None:
        print_kv("project_id", result.project_id)
