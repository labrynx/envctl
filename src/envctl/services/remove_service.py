"""Remove service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import RemovePlan, RemoveVariableResult
from envctl.domain.project import ProjectContext
from envctl.errors import ValidationError
from envctl.repository.contract_repository import load_contract, write_contract
from envctl.services.context_service import load_project_context
from envctl.services.profile_service import run_profile_list
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import build_profile_env_path, normalize_profile_name


def _write_profile_values(path: Path, values: dict[str, str]) -> None:
    """Persist one profile values file."""
    ensure_dir(path.parent)
    write_text_atomic(path, dump_env(values))


def _remove_key_from_profile(path: Path, key: str) -> bool:
    """Remove one key from one physical profile file."""
    values = load_env_file(path)
    if key not in values:
        return False

    values.pop(key, None)
    _write_profile_values(path, values)
    return True


def plan_remove(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, RemovePlan]:
    """Plan the effects of removing one variable globally."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract = load_contract(context.repo_contract_path)
    declared_in_contract = key in contract.variables

    _profile_context, profile_list = run_profile_list(resolved_profile)
    active_profile_path = build_profile_env_path(context.vault_project_dir, resolved_profile)
    present_in_active_profile = key in load_env_file(active_profile_path)

    other_profiles: list[str] = []
    for profile in profile_list.profiles:
        if profile == resolved_profile:
            continue

        path = build_profile_env_path(context.vault_project_dir, profile)
        if key in load_env_file(path):
            other_profiles.append(profile)

    return context, RemovePlan(
        key=key,
        declared_in_contract=declared_in_contract,
        present_in_active_profile=present_in_active_profile,
        present_in_other_profiles=tuple(other_profiles),
    )


def run_remove(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, RemoveVariableResult]:
    """Remove one variable from the contract and from all persisted profiles."""
    _config, context = load_project_context()

    contract = load_contract(context.repo_contract_path)
    if key not in contract.variables:
        raise ValidationError(f"Key is not declared in the contract: {key}")

    updated_contract = contract.without_variable(key)
    write_contract(context.repo_contract_path, updated_contract)

    _profile_context, profile_list = run_profile_list(active_profile)
    removed_from_profiles: list[str] = []
    affected_paths: list[Path] = []

    for profile in profile_list.profiles:
        path = build_profile_env_path(context.vault_project_dir, profile)
        if _remove_key_from_profile(path, key):
            removed_from_profiles.append(profile)
            affected_paths.append(path)

    return context, RemoveVariableResult(
        key=key,
        removed_from_contract=True,
        removed_from_profiles=tuple(removed_from_profiles),
        repo_contract_path=context.repo_contract_path,
        affected_paths=tuple(affected_paths),
    )
