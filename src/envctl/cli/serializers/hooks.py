"""Managed hooks serializers."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.common import path_to_str
from envctl.domain.hooks import HookInspectionResult, HookOperationReport, HooksStatusReport


def serialize_hooks_status_report(report: HooksStatusReport) -> dict[str, Any]:
    """Serialize one managed hooks status report."""
    return {
        "hooks_path": path_to_str(report.hooks_path),
        "overall_status": report.overall_status.value,
        "results": [serialize_hook_inspection_result(result) for result in report.results],
        "details": list(report.details),
    }


def serialize_hook_operation_report(report: HookOperationReport) -> dict[str, Any]:
    """Serialize one managed hooks operation report."""
    return {
        "hooks_path": path_to_str(report.hooks_path),
        "overall_status": report.final_status.value,
        "changed": report.changed,
        "results": [
            {
                "hook_name": result.name.value,
                "path": path_to_str(result.path),
                "before_status": result.before_status.value,
                "status": result.after_status.value,
                "action": result.action.value,
                "changed": result.changed,
                "managed": result.managed,
                "details": list(result.details),
            }
            for result in report.results
        ],
        "details": list(report.details),
    }


def serialize_hook_inspection_result(result: HookInspectionResult) -> dict[str, Any]:
    """Serialize one managed hook inspection result."""
    return {
        "hook_name": result.name.value,
        "path": path_to_str(result.path),
        "status": result.status.value,
        "managed": result.managed,
        "is_executable": result.is_executable,
        "details": list(result.details),
    }
