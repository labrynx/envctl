"""Remove service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import RemoveResult
from envctl.domain.project import ConfirmFn, ProjectContext
from envctl.repository.contract_repository import (
    load_contract_optional,
    remove_variable,
    write_contract,
)
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions


def run_remove(
    key: str,
    *,
    yes: bool = False,
    confirm: ConfirmFn | None = None,
) -> tuple[ProjectContext, RemoveResult]:
    """Remove one key from vault and contract."""
    _config, context = load_project_context()

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    contract = load_contract_optional(context.repo_contract_path)
    has_contract_entry = contract is not None and key in contract.variables

    if has_contract_entry and not yes and confirm is not None:
        approved = confirm(f"Remove '{key}' from both local vault and contract?", False)
        if not approved:
            return context, RemoveResult(
                key=key,
                removed_from_vault=False,
                removed_from_contract=False,
            )

    data = load_env_file(context.vault_values_path)
    removed_from_vault = key in data
    data.pop(key, None)
    write_text_atomic(context.vault_values_path, dump_env(data))
    ensure_private_file_permissions(context.vault_values_path)

    removed_from_contract = False
    if has_contract_entry and contract is not None:
        updated_contract = remove_variable(contract, key)
        write_contract(context.repo_contract_path, updated_contract)
        removed_from_contract = True

    return context, RemoveResult(
        key=key,
        removed_from_vault=removed_from_vault,
        removed_from_contract=removed_from_contract,
    )
