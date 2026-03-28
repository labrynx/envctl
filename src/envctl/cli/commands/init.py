"""Init command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.init_service import run_init
from envctl.utils.output import print_kv, print_success


@handle_errors
def init_command(project: str | None = typer.Argument(default=None)) -> None:
    """Initialize the current project in the local vault."""
    context = run_init(project_name=project)
    print_success(f"Initialized {context.display_name}")
    print_kv("repo_root", str(context.repo_root))
    print_kv("contract", str(context.repo_contract_path))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_values", str(context.vault_values_path))
