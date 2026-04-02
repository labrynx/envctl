"""Remove service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.operations import RemovePlan, RemoveVariableResult
from envctl.domain.project import ProjectContext
from envctl.errors import ValidationError
from envctl.repository.contract_repository import load_contract, write_contract
from envctl.repository.profile_repository import (
    list_persisted_profiles,
    load_profile_values,
    remove_key_from_profile,
)
from envctl.services.context_service import load_project_context
from envctl.utils.project_paths import normalize_profile_name


def plan_remove(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, RemovePlan]:
    """Plan the effects of removing one variable globally."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract = load_contract(context.repo_contract_path)
    declared_in_contract = key in contract.variables

    _resolved_profile, _active_profile_path, active_values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )
    present_in_active_profile = key in active_values

    other_profiles: list[str] = []
    absent_other_profiles: list[str] = []
    for profile in list_persisted_profiles(context):
        if profile == resolved_profile:
            continue

        _resolved_profile, _path, values = load_profile_values(context, profile)
        if key in values:
            other_profiles.append(profile)
        else:
            absent_other_profiles.append(profile)

    return context, RemovePlan(
        key=key,
        declared_in_contract=declared_in_contract,
        present_in_active_profile=present_in_active_profile,
        present_in_other_profiles=tuple(other_profiles),
        absent_in_other_profiles=tuple(absent_other_profiles),
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

    _resolved_profile, _active_profile_path, _active_values = load_profile_values(
        context,
        active_profile,
        require_existing_explicit=True,
    )
    persisted_profiles = list_persisted_profiles(context)
    inspected_profiles: list[str] = []
    removed_from_profiles: list[str] = []
    missing_from_profiles: list[str] = []
    affected_paths: list[Path] = []

    for profile in persisted_profiles:
        inspected_profiles.append(profile)
        _resolved_profile, path, removed = remove_key_from_profile(context, profile, key)
        if removed:
            removed_from_profiles.append(profile)
            affected_paths.append(path)
        else:
            missing_from_profiles.append(profile)

    return context, RemoveVariableResult(
        key=key,
        removed_from_contract=True,
        inspected_profiles=tuple(inspected_profiles),
        removed_from_profiles=tuple(removed_from_profiles),
        missing_from_profiles=tuple(missing_from_profiles),
        repo_contract_path=context.repo_contract_path,
        affected_paths=tuple(affected_paths),
    )
