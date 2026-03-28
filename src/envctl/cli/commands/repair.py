"""Repair command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors
from envctl.services.repair_service import run_repair
from envctl.utils.output import print_kv, print_success


@handle_errors
def repair_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
) -> None:
    """Repair the repository env symlink using existing envctl metadata."""
    context = run_repair(force=yes, confirm=typer_confirm)
    print_success(f"Repaired project '{context.project_slug}'")
    print_kv("project_slug", context.project_slug)
    print_kv("project_id", context.project_id)
    print_kv("repo_env", str(context.repo_env_path))
    print_kv("vault_env", str(context.vault_env_path))
