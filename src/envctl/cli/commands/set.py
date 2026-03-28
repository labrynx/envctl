"""Set command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.set_service import run_set
from envctl.utils.output import print_kv, print_success


@handle_errors
def set_command(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
) -> None:
    """Create or update a key in the managed vault env file."""
    context = run_set(key=key, value=value)
    print_success(f"Updated key '{key}' for project '{context.project_name}'")
    print_kv("vault_env", str(context.vault_env_path))
