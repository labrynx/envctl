"""Sync command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.runtime import get_active_profile
from envctl.services.sync_service import run_sync
from envctl.utils.output import print_kv, print_success


@handle_errors
@requires_writable_runtime("sync")
def sync_command() -> None:
    """Materialize the resolved environment into the repository env file."""
    _context, active_profile, target_path = run_sync(get_active_profile())

    print_success("Synced generated environment")
    print_kv("profile", active_profile)
    print_kv("target", str(target_path))
