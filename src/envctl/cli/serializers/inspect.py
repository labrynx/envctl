"""Serializers for inspect output."""

from __future__ import annotations

from typing import Any

from envctl.cli.compat.legacy_json import serialize_legacy_inspect_report
from envctl.cli.serializers.context import serialize_project_context
from envctl.cli.serializers.resolution import serialize_resolved_value
from envctl.domain.diagnostics import (
    DiagnosticProblem,
    InspectContractGraph,
    InspectKeyResult,
    InspectResult,
)


def _serialize_problem(problem: DiagnosticProblem) -> dict[str, Any]:
    """Serialize one diagnostic problem."""
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def _serialize_contract_graph(graph: InspectContractGraph) -> dict[str, Any]:
    """Serialize one inspect contract graph."""
    return {
        "root_path": str(graph.root_path),
        "contract_paths": [str(path) for path in graph.contract_paths],
        "contracts_total": graph.contracts_total,
        "variables_total": graph.variables_total,
        "sets_total": graph.sets_total,
        "groups_total": graph.groups_total,
        "import_graph": {
            str(path): [str(child) for child in children]
            for path, children in graph.import_graph.items()
        },
        "declared_in": {key: str(path) for key, path in graph.declared_in.items()},
        "sets_index": {key: list(value) for key, value in graph.sets_index.items()},
        "groups_index": {key: list(value) for key, value in graph.groups_index.items()},
    }


def serialize_inspect_result(result: InspectResult) -> dict[str, Any]:
    """Serialize one inspect result."""
    return {
        "project": {
            "repo_root": str(result.project.repo_root),
            "project_slug": result.project.project_slug,
            "project_id": result.project.project_id,
            "binding_source": result.project.binding_source,
            "vault_dir": str(result.project.vault_project_dir),
        },
        "runtime": {
            "active_profile": result.active_profile,
            "selection": {
                "mode": result.selection.mode,
                "group": result.selection.group,
                "set": result.selection.set_name,
                "var": result.selection.variable,
            },
            "contract_path": result.contract_path,
            "values_path": result.values_path,
        },
        "contract_graph": _serialize_contract_graph(result.contract_graph),
        "summary": {
            "total": result.summary.total,
            "valid": result.summary.valid,
            "invalid": result.summary.invalid,
            "unknown": result.summary.unknown,
        },
        "variables": {item.key: serialize_resolved_value(item) for item in result.variables},
        "problems": [_serialize_problem(problem) for problem in result.problems],
        "context": serialize_project_context(result.project),
        "report": serialize_legacy_inspect_report(result),  # legacy JSON compatibility
    }


def serialize_inspect_key_result(result: InspectKeyResult) -> dict[str, Any]:
    """Serialize one inspect-key result."""
    return {
        "active_profile": result.active_profile,
        "context": serialize_project_context(result.project),
        "item": serialize_resolved_value(result.item),
        "contract": {
            "declared_in": str(result.declared_in),
            "type": result.contract_type,
            "format": result.contract_format,
            "sets": list(result.sets),
            "groups": list(result.groups),
            "default": result.default,
            "sensitive": result.sensitive,
        },
    }
