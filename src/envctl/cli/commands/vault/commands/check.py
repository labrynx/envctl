"""Vault check command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import build_vault_check_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
def vault_check_command() -> None:
    """Check the local vault file as a physical artifact."""
    from envctl.services.vault_service import run_vault_check

    _context, active_profile, result = run_vault_check(get_active_profile())

    present(
        build_vault_check_output(
            profile=active_profile,
            path=result.path,
            exists=result.exists,
            parseable=result.parseable,
            private_permissions=result.private_permissions,
            key_count=result.key_count,
            state=result.state,
            detail=result.detail,
        ),
        output_format="json" if is_json_output() else "text",
    )

    if (
        not result.exists
        or not result.parseable
        or not result.private_permissions
        or result.state in {"plaintext", "wrong_key", "corrupt"}
    ):
        raise typer.Exit(code=1)
