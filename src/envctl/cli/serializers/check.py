"""Serializers for check output."""

from __future__ import annotations

from typing import Any

from envctl.cli.compat.legacy_json import serialize_legacy_check_report
from envctl.cli.serializers.context import serialize_project_context
from envctl.domain.diagnostics import CheckResult, DiagnosticProblem
from envctl.domain.project import ProjectContext


def serialize_problem(problem: DiagnosticProblem) -> dict[str, Any]:
    """Serialize one diagnostic problem."""
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def serialize_check_result(
    result: CheckResult,
    *,
    context: ProjectContext | None = None,
) -> dict[str, Any]:
    """Serialize one check result."""
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
        "report": serialize_legacy_check_report(result),  # legacy JSON compatibility
    }
    if context is not None:
        payload["context"] = serialize_project_context(context)
    return payload
