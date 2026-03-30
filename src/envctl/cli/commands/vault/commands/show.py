"""Vault show command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm
from envctl.cli.decorators import handle_errors, text_output_only
from envctl.cli.runtime import get_active_profile
from envctl.repository.contract_repository import load_contract_optional
from envctl.services.vault_service import run_vault_show
from envctl.utils.masking import mask_value
from envctl.utils.output import print_kv, print_warning

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
@text_output_only("vault show")
def vault_show_command(
    raw: bool = RAW_OPTION,
    profile: str | None = PROFILE_OPTION,
) -> None:
    """Show the current vault file contents, masked by default."""
    selected_profile = profile or get_active_profile()
    context, active_profile, result = run_vault_show(selected_profile)

    if not result.exists:
        print_warning("Vault file does not exist")
        print_kv("profile", active_profile)
        print_kv("vault_values", str(result.path))
        raise typer.Exit(code=1)

    print_kv("profile", active_profile)
    print_kv("vault_values", str(result.path))

    if not result.values:
        print_warning("Vault file is empty")
        return

    if raw:
        approved = typer_confirm(
            "This will display unmasked secret values. Continue?",
            default=False,
        )
        if not approved:
            print_warning("Nothing was shown.")
            return

    contract = load_contract_optional(context.repo_contract_path)
    contract_variables = contract.variables if contract is not None else {}

    typer.echo("Values:")
    for key in sorted(result.values):
        value = result.values[key]
        spec = contract_variables.get(key)
        rendered = _render_vault_value(
            raw=raw,
            value=value,
            sensitive=spec is None or spec.sensitive,
        )
        typer.echo(f"  {key}={rendered}")
