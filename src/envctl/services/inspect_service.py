"""Inspect service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import (
    CommandWarning,
    InspectContractGraph,
    InspectKeyResult,
    InspectResult,
)
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.errors import ContractError, ValidationError
from envctl.repository.contract_composition import (
    ResolvedContractBundle,
    load_resolved_contract_bundle,
)
from envctl.services.context_service import load_project_context
from envctl.services.contract_selection_service import filter_resolution_report
from envctl.services.resolution_diagnostics import (
    build_diagnostic_problems,
    build_diagnostic_summary,
)
from envctl.services.resolution_service import resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def _build_contract_graph_summary(bundle: ResolvedContractBundle) -> InspectContractGraph:
    """Build the inspect-facing summary of the composed contract graph."""
    graph = bundle.graph
    return InspectContractGraph(
        root_path=graph.root_path,
        contract_paths=graph.contract_paths,
        contracts_total=len(graph.contract_paths),
        variables_total=len(graph.variables),
        sets_total=len(graph.sets_index),
        groups_total=len(graph.groups_index),
        import_graph=graph.import_graph,
        declared_in=graph.declared_in,
        sets_index=graph.sets_index,
        groups_index=graph.groups_index,
    )


def run_inspect(
    active_profile: str | None = None,
    *,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, InspectResult, tuple[ContractDeprecationWarning, ...]]:
    """Inspect the resolved environment."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    bundle = load_resolved_contract_bundle(context.repo_root)
    contract = bundle.contract
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
        contract_graph=_build_contract_graph_summary(bundle),
        warnings=tuple(bundle.command_warnings) + tuple(context.runtime_warnings),
    )
    return context, result, bundle.warnings


def run_inspect_key(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, InspectKeyResult, tuple[ContractDeprecationWarning, ...]]:
    """Inspect one resolved key in detail."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    bundle = load_resolved_contract_bundle(context.repo_root)
    contract = bundle.contract
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    try:
        item = report.values[key]
    except KeyError as exc:
        raise ValidationError(f"Key is not resolved: {key}") from exc

    spec = contract.variables.get(key)
    if spec is None:
        raise ValidationError(f"Key is not declared in the contract: {key}")

    graph = bundle.graph
    effective_sets = tuple(name for name, keys in graph.sets_index.items() if key in keys)
    declared_in = graph.declared_in.get(key, context.repo_contract_path)

    result = InspectKeyResult(
        project=context,
        active_profile=resolved_profile,
        item=item,
        contract_type=spec.type,
        contract_format=spec.format,
        declared_in=declared_in,
        sets=effective_sets,
        groups=spec.normalized_groups,
        default=spec.default,
        sensitive=spec.sensitive,
        warnings=tuple(bundle.command_warnings)
        + tuple(context.runtime_warnings)
        + tuple(
            CommandWarning(kind="invalid_value", message=item.detail)
            for _ in [0]
            if item.detail and not item.valid
        ),
    )
    return context, result, bundle.warnings


def ensure_known_contract_set(result: InspectResult, name: str) -> tuple[str, ...]:
    """Return one known set membership list or raise a stable error."""
    normalized = name.strip()
    try:
        return result.contract_graph.sets_index[normalized]
    except KeyError as exc:
        available = ", ".join(sorted(result.contract_graph.sets_index)) or "none"
        raise ContractError(f'Set "{normalized}" not found. Available sets: {available}') from exc


def ensure_known_contract_group(result: InspectResult, name: str) -> tuple[str, ...]:
    """Return one known group membership list or raise a stable error."""
    normalized = name.strip()
    try:
        return result.contract_graph.groups_index[normalized]
    except KeyError as exc:
        available = ", ".join(sorted(result.contract_graph.groups_index)) or "none"
        raise ContractError(
            f'Group "{normalized}" not found. Available groups: {available}'
        ) from exc
