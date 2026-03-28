"""Init command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.init_service import run_init
from envctl.utils.output import print_kv, print_success


@handle_errors
def init_command(project: str | None = typer.Argument(default=None)) -> None:
    """Initialize the current Git repository in the vault and link its env file."""
    context = run_init(project_name=project)
    print_success(f"Initialized project '{context.project_slug}'")
    print_kv("project_slug", context.project_slug)
    print_kv("project_id", context.project_id)
    print_kv("repo_root", str(context.repo_root))
    print_kv("metadata", str(context.repo_metadata_path))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_env", str(context.vault_env_path))
    print_kv("repo_env", str(context.repo_env_path))
