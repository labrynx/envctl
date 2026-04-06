"""Serializers for inspect output."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.context import serialize_project_context
from envctl.cli.serializers.resolution import serialize_resolved_value
from envctl.domain.diagnostics import DiagnosticProblem, InspectKeyResult, InspectResult


def _serialize_problem(problem: DiagnosticProblem) -> dict[str, Any]:
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def _serialize_legacy_report(result: InspectResult) -> dict[str, Any]:
    missing_required = [
        problem.key for problem in result.problems if problem.kind == "missing_required"
    ]
    invalid_keys = [
        problem.key
        for problem in result.problems
        if problem.kind in {"invalid_value", "expansion_reference_error"}
    ]
    unknown_keys = [problem.key for problem in result.problems if problem.kind == "unknown_key"]
    return {
        "is_valid": result.summary.invalid == 0,
        "values": {item.key: serialize_resolved_value(item) for item in result.variables},
        "missing_required": missing_required,
        "unknown_keys": unknown_keys,
        "invalid_keys": invalid_keys,
    }


def serialize_inspect_result(result: InspectResult) -> dict[str, Any]:
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
        "summary": {
            "total": result.summary.total,
            "valid": result.summary.valid,
            "invalid": result.summary.invalid,
            "unknown": result.summary.unknown,
        },
        "variables": {item.key: serialize_resolved_value(item) for item in result.variables},
        "problems": [_serialize_problem(problem) for problem in result.problems],
        "context": serialize_project_context(result.project),
        "report": _serialize_legacy_report(result),
    }


def serialize_inspect_key_result(result: InspectKeyResult) -> dict[str, Any]:
    return {
        "active_profile": result.active_profile,
        "context": serialize_project_context(result.project),
        "item": serialize_resolved_value(result.item),
        "contract": {
            "type": result.contract_type,
            "format": result.contract_format,
            "groups": list(result.groups),
            "default": result.default,
            "sensitive": result.sensitive,
        },
    }
