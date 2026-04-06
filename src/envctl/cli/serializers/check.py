"""Serializers for check output."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.context import serialize_project_context
from envctl.cli.serializers.resolution import serialize_resolved_value
from envctl.domain.diagnostics import CheckResult, DiagnosticProblem
from envctl.domain.project import ProjectContext


def serialize_problem(problem: DiagnosticProblem) -> dict[str, Any]:
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def _serialize_legacy_report(result: CheckResult) -> dict[str, Any]:
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
        "values": {item.key: serialize_resolved_value(item) for item in result.values},
        "missing_required": missing_required,
        "unknown_keys": unknown_keys,
        "invalid_keys": invalid_keys,
    }


def serialize_check_result(
    result: CheckResult,
    *,
    context: ProjectContext | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "active_profile": result.active_profile,
        "selection": {
            "mode": result.selection.mode,
            "group": result.selection.group,
            "set": result.selection.set_name,
            "var": result.selection.variable,
        },
        "summary": {
            "total": result.summary.total,
            "valid": result.summary.valid,
            "invalid": result.summary.invalid,
            "unknown": result.summary.unknown,
        },
        "problems": [serialize_problem(problem) for problem in result.problems],
        "report": _serialize_legacy_report(result),
    }
    if context is not None:
        payload["context"] = serialize_project_context(context)
    return payload
