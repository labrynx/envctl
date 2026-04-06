"""Legacy JSON serializers kept for backward compatibility."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.resolution import serialize_resolved_value
from envctl.domain.diagnostics import CheckResult, InspectResult


def serialize_legacy_check_report(result: CheckResult) -> dict[str, Any]:
    """Serialize the legacy check report kept for JSON compatibility."""
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


def serialize_legacy_inspect_report(result: InspectResult) -> dict[str, Any]:
    """Serialize the legacy inspect report kept for JSON compatibility."""
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
