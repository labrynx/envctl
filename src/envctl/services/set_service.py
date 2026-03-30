"""Set service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import SetResult
from envctl.domain.project import ProjectContext
from envctl.errors import ContractError
from envctl.repository.contract_repository import load_contract_optional
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir


def run_set(key: str, value: str) -> tuple[ProjectContext, SetResult]:
    """Create or update one explicit key in the vault values file only."""
    _config, context = load_project_context(persist_binding=True)

    ensure_dir(context.vault_project_dir)

    data = load_env_file(context.vault_values_path)
    existed = key in data
    data[key] = value

    write_text_atomic(context.vault_values_path, dump_env(data))

    declared_in_contract = False
    try:
        contract = load_contract_optional(context.repo_contract_path)
        declared_in_contract = contract is not None and key in contract.variables
    except ContractError:
        declared_in_contract = False

    return context, SetResult(
        key=key,
        created=not existed,
        updated=existed,
        declared_in_contract=declared_in_contract,
    )