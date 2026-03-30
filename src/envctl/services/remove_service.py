"""Remove service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import RemoveResult
from envctl.domain.project import ProjectContext
from envctl.repository.contract_repository import (
    load_contract_optional,
    write_contract,
)
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir


def run_remove(key: str) -> tuple[ProjectContext, RemoveResult]:
    """Remove one key from vault and contract."""
    _config, context = load_project_context(persist_binding=True)

    ensure_dir(context.vault_project_dir)

    contract = load_contract_optional(context.repo_contract_path)
    has_contract_entry = contract is not None and key in contract.variables

    data = load_env_file(context.vault_values_path)
    removed_from_vault = key in data
    data.pop(key, None)
    write_text_atomic(context.vault_values_path, dump_env(data))

    removed_from_contract = False
    if has_contract_entry and contract is not None:
        updated_contract = contract.without_variable(key)
        write_contract(context.repo_contract_path, updated_contract)
        removed_from_contract = True

    return context, RemoveResult(
        key=key,
        removed_from_vault=removed_from_vault,
        removed_from_contract=removed_from_contract,
    )