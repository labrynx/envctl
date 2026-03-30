"""Rebind command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors
from envctl.services.rebind_service import run_rebind
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def project_rebind_command(
    new_project: bool = typer.Option(
        False,
        "--new-project",
        help="Generate a fresh canonical project id and bind this checkout to it.",
    ),
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
    if not new_project:
        raise typer.BadParameter("Use --new-project to create a fresh project binding.")

    if not yes:
        approved = typer_confirm(
            "This will generate a new project identity for the current checkout. Continue?",
            False,
        )
        if not approved:
            print_warning("Nothing was changed.")
            return

    context, result = run_rebind(copy_values=copy_values)

    print_success(f"Rebound repository to {context.display_name}")
    if result.previous_project_id is not None:
        print_kv("previous_project_id", result.previous_project_id)
    print_kv("new_project_id", result.new_project_id)
    print_kv("copied_values", "yes" if result.copied_values else "no")
    print_kv("repo_root", str(context.repo_root))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_values", str(context.vault_values_path))
