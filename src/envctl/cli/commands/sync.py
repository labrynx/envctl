"""Sync command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.services.sync_service import run_sync
from envctl.utils.output import print_kv, print_success


@handle_errors
def sync_command() -> None:
    """Materialize the resolved environment into the repository file."""
    context, _report = run_sync()
    print_success(f"Synced generated environment for {context.display_name}")
    print_kv("repo_env", str(context.repo_env_path))
