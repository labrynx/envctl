"""Vault check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.presenters import render_vault_check_result
from envctl.cli.runtime import get_active_profile
from envctl.services.vault_service import run_vault_check


@handle_errors
@text_output_only("vault check")
def vault_check_command() -> None:
    """Check the local vault file as a physical artifact."""
    _context, active_profile, result = run_vault_check(get_active_profile())

    render_vault_check_result(
        profile=active_profile,
        path=result.path,
        exists=result.exists,
        parseable=result.parseable,
        private_permissions=result.private_permissions,
        key_count=result.key_count,
    )

    if not result.exists or not result.parseable or not result.private_permissions:
        raise typer.Exit(code=1)
