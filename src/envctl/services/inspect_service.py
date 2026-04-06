"""Inspect service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning, InspectKeyResult, InspectResult
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.errors import ValidationError
from envctl.repository.contract_repository import load_contract_with_warnings
from envctl.services.context_service import load_project_context
from envctl.services.contract_selection_service import filter_resolution_report
from envctl.services.resolution_diagnostics import (
    build_diagnostic_problems,
    build_diagnostic_summary,
)
from envctl.services.resolution_service import resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def run_inspect(
    active_profile: str | None = None,
    *,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, InspectResult, tuple[ContractDeprecationWarning, ...]]:
    """Inspect the resolved environment."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    contract, warnings = load_contract_with_warnings(context.repo_contract_path)
    report = resolve_environment(context, contract, active_profile=resolved_profile)
    active_selection = selection or ContractSelection()
    filtered_report = filter_resolution_report(report, contract, selection=active_selection)

    result = InspectResult(
        project=context,
        active_profile=resolved_profile,
        selection=active_selection,
        contract_path=str(context.repo_contract_path),
        values_path=str(context.vault_values_path),
        summary=build_diagnostic_summary(filtered_report),
        variables=tuple(filtered_report.values[key] for key in sorted(filtered_report.values)),
        problems=build_diagnostic_problems(filtered_report),
    )
    return context, result, warnings


def run_inspect_key(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, InspectKeyResult, tuple[ContractDeprecationWarning, ...]]:
    """Inspect one resolved key in detail."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    contract, warnings = load_contract_with_warnings(context.repo_contract_path)
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    try:
        item = report.values[key]
    except KeyError as exc:
        raise ValidationError(f"Key is not resolved: {key}") from exc

    spec = contract.variables.get(key)
    if spec is None:
        raise ValidationError(f"Key is not declared in the contract: {key}")

    result = InspectKeyResult(
        project=context,
        active_profile=resolved_profile,
        item=item,
        contract_type=spec.type,
        contract_format=spec.format,
        groups=spec.normalized_groups,
        default=spec.default,
        sensitive=spec.sensitive,
        warnings=tuple(
            CommandWarning(kind="invalid_value", message=item.detail)
            for _ in [0]
            if item.detail and not item.valid
        ),
    )
    return context, result, warnings
