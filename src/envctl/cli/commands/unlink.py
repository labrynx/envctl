"""Unlink command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.services.unlink_service import run_unlink
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def unlink_command() -> None:
    """Remove the repository symlink only."""
    result = run_unlink()

    if result.removed:
        print_success(f"Unlinked repository env file for '{result.context.project_name}'")
    else:
        print_warning(result.message)

    print_kv("repo_env", str(result.context.repo_env_path))
    print_kv("vault_env", str(result.context.vault_env_path))
