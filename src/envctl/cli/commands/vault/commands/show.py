"""Vault show command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.vault import (
    build_vault_show_cancelled_output,
    build_vault_show_empty_output,
    build_vault_show_missing_output,
    build_vault_show_values_output,
)
from envctl.cli.prompts.confirmation_prompts import build_vault_show_raw_confirmation_message
from envctl.cli.prompts.input import confirm
from envctl.cli.runtime import get_active_profile, is_json_output
from envctl.domain.runtime import OutputFormat
from envctl.utils.masking import mask_value

RAW_OPTION = typer.Option(
    False,
    "--raw",
    help="Show unmasked values.",
)
PROFILE_OPTION = typer.Option(
    None,
    "--profile",
    "-p",
    help="Inspect a specific profile without changing the global CLI profile.",
)


def _render_vault_value(
    *,
    raw: bool,
    value: str,
    sensitive: bool,
) -> str:
    """Render one vault value for terminal output."""
    return value if raw else mask_value(value) if sensitive else value


@handle_errors
def vault_show_command(
    raw: bool = RAW_OPTION,
    profile: str | None = PROFILE_OPTION,
) -> None:
    """Show the current vault file contents, masked by default."""
    selected_profile = profile or get_active_profile()

    from envctl.services.vault_service import run_vault_show

    _context, active_profile, result = run_vault_show(selected_profile)
    output_format: OutputFormat = OutputFormat.JSON if is_json_output() else OutputFormat.TEXT

    if not result.exists:
        present(
            build_vault_show_missing_output(
                profile=active_profile,
                path=result.path,
            ),
            output_format=output_format,
        )
        raise typer.Exit(code=1)

    if not result.values:
        present(
            build_vault_show_empty_output(
                profile=active_profile,
                path=result.path,
            ),
            output_format=output_format,
        )
        return

    if raw:
        approved = confirm(
            build_vault_show_raw_confirmation_message(),
            default=False,
        )
        if not approved:
            present(
                build_vault_show_cancelled_output(
                    profile=active_profile,
                    path=result.path,
                ),
                output_format=output_format,
            )
            return

    rendered_values: dict[str, str] = {}
    for key in sorted(result.values):
        value = result.values[key]
        sensitive = result.sensitive_keys.get(key, True)
        rendered_values[key] = _render_vault_value(
            raw=raw,
            value=value,
            sensitive=sensitive,
        )

    present(
        build_vault_show_values_output(
            profile=active_profile,
            path=result.path,
            values=rendered_values,
            state=result.state,
            detail=result.detail,
        ),
        output_format=output_format,
    )
