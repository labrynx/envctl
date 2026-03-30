"""Init command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.init_service import InitContractMode, run_init
from envctl.utils.output import print_kv, print_success, print_warning

CONTRACT_OPTION = typer.Option(
    "ask",
    "--contract",
    help="How to handle a missing contract: ask, example, starter, or skip.",
)


def typer_confirm(message: str, default: bool) -> bool:
    """Bridge confirmations from services to Typer."""
    return typer.confirm(message, default=default)


@handle_errors
def init_command(
    project: str | None = typer.Argument(default=None),
    contract: InitContractMode = CONTRACT_OPTION,
) -> None:
    """Initialize the current project in the local vault."""
    context, init_result = run_init(
        project_name=project,
        contract_mode=contract,
        confirm=typer_confirm,
    )

    print_success(f"Initialized {context.display_name}")
    print_kv("project_key", context.project_key)
    print_kv("binding_source", context.binding_source)
    print_kv("repo_root", str(context.repo_root))
    print_kv("contract", str(context.repo_contract_path))
    print_kv("vault_dir", str(context.vault_project_dir))
    print_kv("vault_values", str(context.vault_values_path))
    print_kv("vault_state", str(context.vault_state_path))

    if init_result.contract_created:
        print_kv("contract_created", "yes")
        print_kv("contract_template", init_result.contract_template or "custom")
    elif init_result.contract_skipped:
        print_warning("No contract file was created")