"""Vault path command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import build_vault_path_output
from envctl.cli.runtime import get_active_profile, is_json_output


@handle_errors
def vault_path_command() -> None:
    """Print the current vault file path."""
    from envctl.services.vault_service import run_vault_path

    _context, active_profile, path = run_vault_path(get_active_profile())

    present(
        build_vault_path_output(
            profile=active_profile,
            path=path,
        ),
        output_format="json" if is_json_output() else "text",
    )
