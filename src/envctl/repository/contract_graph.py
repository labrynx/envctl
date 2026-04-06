"""Contract graph resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envctl.constants import LEGACY_CONTRACT_FILENAME, PRIMARY_CONTRACT_FILENAME
from envctl.domain.contract import Contract
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.errors import ContractError
from envctl.repository.contract_repository import load_contract_with_warnings
from envctl.services.error_diagnostics import ContractDiagnosticIssue, ContractDiagnostics


@dataclass(frozen=True)
class ResolvedContractLoad:
    """Resolved raw contracts and import graph."""

    root_path: Path
    contracts: tuple[Contract, ...]
    contract_paths: tuple[Path, ...]
    import_graph: dict[Path, tuple[Path, ...]]
    warnings: tuple[ContractDeprecationWarning, ...]


_RESERVED_ROOT_NAMES = {PRIMARY_CONTRACT_FILENAME, LEGACY_CONTRACT_FILENAME}


def resolve_contract_graph(root_path: Path, *, repo_root: Path) -> ResolvedContractLoad:
    """Resolve all imported contracts from one discovered root contract."""
    visited: set[Path] = set()
    stack: list[Path] = []
    ordered_paths: list[Path] = []
    ordered_contracts: list[Contract] = []
    graph: dict[Path, tuple[Path, ...]] = {}
    warnings: list[ContractDeprecationWarning] = []

    def visit(path: Path, *, importer: Path | None = None) -> None:
        resolved_path = path.resolve()

        if importer is not None:
            _validate_not_reserved_root_import(
                imported_path=resolved_path,
                repo_root=repo_root,
                importer_path=importer,
                root_path=root_path.resolve(),
            )

        if resolved_path in stack:
            cycle = tuple((*stack, resolved_path))
            raise ContractError(
                "Contract import cycle detected.",
                diagnostics=ContractDiagnostics(
                    category="contract_import_cycle",
                    path=resolved_path,
                    issues=tuple(
                        ContractDiagnosticIssue(field="cycle", detail=str(item)) for item in cycle
                    ),
                    suggested_actions=("remove the recursive import chain",),
                ),
            )

        if resolved_path in visited:
            return

        stack.append(resolved_path)
        try:
            contract, contract_warnings = load_contract_with_warnings(resolved_path)
        except ContractError as exc:
            diagnostics = exc.diagnostics
            if (
                diagnostics is not None
                and isinstance(diagnostics, ContractDiagnostics)
                and diagnostics.category == "missing_contract_file"
            ):
                raise ContractError(
                    f"Invalid contract import: {resolved_path}",
                    diagnostics=ContractDiagnostics(
                        category="invalid_import_path",
                        path=resolved_path,
                        issues=(
                            ContractDiagnosticIssue(
                                field="importer",
                                detail=str(importer) if importer is not None else str(root_path),
                            ),
                        ),
                        suggested_actions=("fix the import path",),
                    ),
                ) from exc
            raise

        warnings.extend(contract_warnings)
        children: list[Path] = []
        for rel in contract.imports:
            child = (resolved_path.parent / rel).resolve()
            children.append(child)
            visit(child, importer=resolved_path)

        graph[resolved_path] = tuple(children)
        stack.pop()
        visited.add(resolved_path)
        ordered_paths.append(resolved_path)
        ordered_contracts.append(contract)

    visit(root_path.resolve())
    return ResolvedContractLoad(
        root_path=root_path.resolve(),
        contracts=tuple(ordered_contracts),
        contract_paths=tuple(ordered_paths),
        import_graph=graph,
        warnings=_dedupe_warnings(warnings),
    )


def _validate_not_reserved_root_import(
    *,
    imported_path: Path,
    repo_root: Path,
    importer_path: Path,
    root_path: Path,
) -> None:
    candidate_paths = {
        (repo_root / PRIMARY_CONTRACT_FILENAME).resolve(),
        (repo_root / LEGACY_CONTRACT_FILENAME).resolve(),
    }
    if imported_path not in candidate_paths:
        return
    raise ContractError(
        f"Reserved root contract import is not allowed: {imported_path.name}",
        diagnostics=ContractDiagnostics(
            category="forbidden_root_contract_import",
            path=imported_path,
            issues=(ContractDiagnosticIssue(field="importer", detail=str(importer_path)),),
            suggested_actions=("migrate the contract instead of importing it",),
        ),
    )


def _dedupe_warnings(
    warnings: list[ContractDeprecationWarning],
) -> tuple[ContractDeprecationWarning, ...]:
    seen: set[tuple[str, str]] = set()
    unique: list[ContractDeprecationWarning] = []
    for warning in warnings:
        key = (warning.key, warning.deprecated_field)
        if key in seen:
            continue
        seen.add(key)
        unique.append(warning)
    return tuple(sorted(unique, key=lambda item: (item.key, item.deprecated_field)))
