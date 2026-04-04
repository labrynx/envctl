"""Resolution service implementation."""

from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.repository.contract_repository import load_contract
from envctl.repository.profile_repository import load_profile_values
from envctl.services.resolution_service.builders import build_resolved_value
from envctl.services.resolution_service.expansion import expand_selected_values
from envctl.services.resolution_service.selection import select_contract_values
from envctl.utils.project_paths import is_local_profile, normalize_profile_name


def load_contract_for_context(context: ProjectContext) -> Contract:
    """Load the contract for the current project."""
    return load_contract(context.repo_contract_path)


def resolve_environment(
    context: ProjectContext,
    contract: Contract,
    *,
    active_profile: str | None = None,
) -> ResolutionReport:
    """Resolve environment values from the selected profile and contract defaults."""
    resolved_profile = normalize_profile_name(active_profile)

    _loaded_profile, _profile_env_path, profile_values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )

    profile_source = (
        "vault" if is_local_profile(resolved_profile) else f"profile:{resolved_profile}"
    )

    selected_values, missing_required = select_contract_values(
        contract,
        profile_values=profile_values,
        profile_source=profile_source,
    )

    expansion_results, derived_sensitive = expand_selected_values(
        contract,
        selected_values,
    )

    values: dict[str, ResolvedValue] = {}
    invalid_keys: list[str] = []

    for key, selected in selected_values.items():
        spec = contract.variables[key]
        value, invalid = build_resolved_value(
            key=key,
            spec=spec,
            selected=selected,
            expanded=expansion_results[key],
            derived_sensitive=derived_sensitive.get(key, False),
        )
        values[key] = value
        if invalid:
            invalid_keys.append(key)

    unknown_keys = sorted(set(profile_values) - set(contract.variables))

    return ResolutionReport.from_parts(
        values=values,
        missing_required=sorted(missing_required),
        unknown_keys=unknown_keys,
        invalid_keys=sorted(invalid_keys),
    )
