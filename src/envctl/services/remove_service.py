"""Remove service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import RemovePlan, RemoveResult
from envctl.domain.project import ProjectContext
from envctl.repository.contract_repository import load_contract_optional, write_contract
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir


def plan_remove(key: str) -> tuple[ProjectContext, RemovePlan]:
    """Inspect the current state before removing one key."""
    _config, context = load_project_context()

    contract = load_contract_optional(context.repo_contract_path)
    declared_in_contract = contract is not None and key in contract.variables

    data = load_env_file(context.vault_values_path)
    present_in_vault = key in data

    return context, RemovePlan(
        key=key,
        present_in_vault=present_in_vault,
        declared_in_contract=declared_in_contract,
    )


def run_remove(
    *,
    context: ProjectContext,
    plan: RemovePlan,
    remove_from_contract: bool,
) -> RemoveResult:
    """Remove one key from vault and optionally from contract."""
    ensure_dir(context.vault_project_dir)

    contract = load_contract_optional(context.repo_contract_path)
    has_contract_entry = contract is not None and plan.key in contract.variables

    data = load_env_file(context.vault_values_path)
    removed_from_vault = plan.key in data
    data.pop(plan.key, None)
    write_text_atomic(context.vault_values_path, dump_env(data))

    removed_from_contract = False
    if remove_from_contract and has_contract_entry and contract is not None:
        updated_contract = contract.without_variable(plan.key)
        write_contract(context.repo_contract_path, updated_contract)
        removed_from_contract = True

    return RemoveResult(
        key=plan.key,
        removed_from_vault=removed_from_vault,
        removed_from_contract=removed_from_contract,
    )
