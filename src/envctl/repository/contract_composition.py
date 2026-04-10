"""Contract composition helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from envctl.domain.contract import Contract, ResolvedContractGraph, VariableSpec
from envctl.domain.contract_sets import SetSpec
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning
from envctl.domain.error_diagnostics import ContractDiagnosticIssue, ContractDiagnostics
from envctl.domain.selection_resolution import resolve_variable_names_for_set
from envctl.errors import ContractError
from envctl.observability.timing import observe_span
from envctl.repository.contract_discovery import discover_root_contract_path
from envctl.repository.contract_graph import resolve_contract_graph


@dataclass(frozen=True)
class ResolvedContractBundle:
    """Composed contract plus graph metadata and warnings."""

    contract: Contract
    graph: ResolvedContractGraph
    warnings: tuple[ContractDeprecationWarning, ...]
    command_warnings: tuple[CommandWarning, ...] = ()


class _MergedSetBucket(TypedDict):
    """Mutable intermediate structure used to merge contract sets."""

    description: str | None
    sets: set[str]
    groups: set[str]
    variables: set[str]


def load_resolved_contract_bundle(repo_root: Path) -> ResolvedContractBundle:
    """Load the composed contract graph for one repository root."""
    with observe_span(
        "contract.compose",
        module=__name__,
        operation="load_resolved_contract_bundle",
    ) as span_fields:
        discovery = discover_root_contract_path(repo_root)
        load = resolve_contract_graph(discovery.path, repo_root=repo_root)
        graph = build_resolved_contract_graph(
            root_path=load.root_path,
            contracts=load.contracts,
            contract_paths=load.contract_paths,
            import_graph=load.import_graph,
        )
        contract = compose_contract_from_graph(load.contracts)
        span_fields["contract_path_count"] = len(graph.contract_paths)
        span_fields["contract_variable_count"] = len(contract.variables)
        span_fields["set_count"] = len(contract.sets)
        span_fields["warning_count"] = len(load.warnings) + len(discovery.warnings)
        return ResolvedContractBundle(
            contract=contract,
            graph=graph,
            warnings=load.warnings,
            command_warnings=discovery.warnings,
        )


def compose_contract_from_graph(contracts: tuple[Contract, ...]) -> Contract:
    """Compose many raw contracts into one merged contract."""
    meta = contracts[-1].meta if contracts else None
    variables, _declared_in = _merge_variables(contracts)
    sets = _merge_sets(contracts)
    return Contract(
        version=1,
        meta=meta,
        imports=(),
        variables=variables,
        sets=sets,
    )


def build_resolved_contract_graph(
    *,
    root_path: Path,
    contracts: tuple[Contract, ...],
    contract_paths: tuple[Path, ...],
    import_graph: dict[Path, tuple[Path, ...]],
) -> ResolvedContractGraph:
    """Build one resolved contract graph model for inspection output."""
    variables, declared_in = _merge_variables(contracts, contract_paths=contract_paths)
    sets = _merge_sets(contracts)
    composed = Contract(
        version=1,
        meta=contracts[-1].meta if contracts else None,
        imports=(),
        variables=variables,
        sets=sets,
    )
    sets_index = {
        name: resolve_variable_names_for_set(composed, name) for name in sorted(composed.sets)
    }
    groups_index = _build_groups_index(variables)
    return ResolvedContractGraph(
        root_path=root_path,
        contract_paths=tuple(sorted(contract_paths)),
        import_graph={
            path: tuple(sorted(children)) for path, children in sorted(import_graph.items())
        },
        variables={key: variables[key] for key in sorted(variables)},
        declared_in={key: declared_in[key] for key in sorted(declared_in)},
        sets_index=sets_index,
        groups_index=groups_index,
    )


def _merge_variables(
    contracts: tuple[Contract, ...],
    *,
    contract_paths: tuple[Path, ...] | None = None,
) -> tuple[dict[str, VariableSpec], dict[str, Path]]:
    """Merge variables from all contracts, enforcing global uniqueness."""
    variables: dict[str, VariableSpec] = {}
    declared_in: dict[str, Path] = {}

    paths = contract_paths or tuple(
        Path(f"<contract:{index}>") for index, _ in enumerate(contracts)
    )

    for path, contract in zip(paths, contracts, strict=False):
        for key, spec in contract.variables.items():
            if key in variables:
                raise ContractError(
                    f"Duplicate variable definition: {key}",
                    diagnostics=ContractDiagnostics(
                        category="duplicate_variable_definition",
                        path=path,
                        key=key,
                        issues=(
                            ContractDiagnosticIssue(
                                field="first_declared_in",
                                detail=str(declared_in[key]),
                            ),
                            ContractDiagnosticIssue(
                                field="duplicate_declared_in",
                                detail=str(path),
                            ),
                        ),
                        suggested_actions=("rename or remove the duplicate variable",),
                    ),
                )
            variables[key] = spec
            declared_in[key] = path

    return variables, declared_in


def _merge_sets(contracts: tuple[Contract, ...]) -> dict[str, SetSpec]:
    """Merge all contract-level sets into one global deterministic mapping."""
    merged: dict[str, _MergedSetBucket] = {}

    for contract in contracts:
        for key, spec in contract.sets.items():
            bucket = merged.setdefault(
                key,
                {
                    "description": spec.description,
                    "sets": set(),
                    "groups": set(),
                    "variables": set(),
                },
            )

            if bucket["description"] is None and spec.description is not None:
                bucket["description"] = spec.description

            bucket["sets"].update(spec.sets)
            bucket["groups"].update(spec.groups)
            bucket["variables"].update(spec.variables)

    result: dict[str, SetSpec] = {}
    for key in sorted(merged):
        bucket = merged[key]
        result[key] = SetSpec(
            name=key,
            description=bucket["description"],
            sets=tuple(sorted(bucket["sets"])),
            groups=tuple(sorted(bucket["groups"])),
            variables=tuple(sorted(bucket["variables"])),
        )

    return result


def _build_groups_index(
    variables: dict[str, VariableSpec],
) -> dict[str, tuple[str, ...]]:
    """Build a deterministic group -> variable index from normalized groups."""
    groups: dict[str, set[str]] = {}

    for key, spec in variables.items():
        for group in spec.normalized_groups:
            groups.setdefault(group, set()).add(key)

    return {name: tuple(sorted(keys)) for name, keys in sorted(groups.items())}
