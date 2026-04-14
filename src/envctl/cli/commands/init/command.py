"""Init command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters.action_presenter import render_init_result
from envctl.services.init_service import InitContractMode

CONTRACT_OPTION = typer.Option(
    "ask",
    "--contract",
    help="How to handle a missing contract: ask, example, starter, or skip.",
)


def typer_confirm(message: str, default: bool) -> bool:
    """Bridge confirmations from services to Typer."""
    return typer.confirm(message, default=default)


@handle_errors
@requires_writable_runtime("init")
@text_output_only("init")
def init_command(
    project: str | None = typer.Argument(default=None),
    contract: InitContractMode = CONTRACT_OPTION,
) -> None:
    """Initialize the current project in the local vault."""
    from envctl.services.init_service import run_init

    context, init_result = run_init(
        project_name=project,
        contract_mode=contract,
        confirm=typer_confirm,
    )

    render_init_result(
        project_key=context.project_key,
        binding_source=context.binding_source,
        repo_root=context.repo_root,
        contract_path=context.repo_contract_path,
        vault_dir=context.vault_project_dir,
        vault_values_path=context.vault_values_path,
        vault_state_path=context.vault_state_path,
        init_result=init_result,
        display_name=context.display_name,
    )
