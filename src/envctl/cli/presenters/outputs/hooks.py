"""Output builders for managed hooks commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from envctl.cli.presenters.common import (
    bullet_item,
    field_item,
    raw_item,
    section,
    success_message,
    warning_message,
)
from envctl.cli.presenters.models import CommandOutput, OutputItem
from envctl.cli.presenters.payloads import path_to_str
from envctl.domain.hooks import (
    HookInspectionResult,
    HookOperationReport,
    HookOperationResult,
    HooksStatusLevel,
    HooksStatusReport,
    HookStatus,
)


def _display_path(path: Path, repo_root: Path) -> str:
    """Build one display path relative to repo root when possible."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _build_hook_inspection_payload(result: HookInspectionResult) -> dict[str, Any]:
    """Build one managed hook inspection payload."""
    return {
        "hook_name": result.name.value,
        "path": path_to_str(result.path),
        "status": result.status.value,
        "managed": result.managed,
        "is_executable": result.is_executable,
        "details": list(result.details),
    }


def _build_hook_operation_payload(result: HookOperationResult) -> dict[str, Any]:
    """Build one managed hook operation payload."""
    return {
        "hook_name": result.name.value,
        "path": path_to_str(result.path),
        "before_status": result.before_status.value,
        "status": result.after_status.value,
        "action": result.action.value,
        "changed": result.changed,
        "managed": result.managed,
        "details": list(result.details),
    }


def _build_inspection_items(
    results: tuple[HookInspectionResult, ...],
    *,
    repo_root: Path,
) -> list[OutputItem]:
    """Build section items for hook inspection results."""
    if not results:
        return [raw_item("No managed hooks were inspected")]

    items: list[OutputItem] = []

    for result in results:
        items.extend(
            [
                field_item("hook", result.name.value),
                field_item("status", result.status.value),
                field_item("path", _display_path(result.path, repo_root)),
                field_item("managed", "yes" if result.managed else "no"),
            ]
        )

        if result.is_executable is not None:
            items.append(field_item("is_executable", "yes" if result.is_executable else "no"))

        if result.details:
            items.extend(bullet_item(detail) for detail in result.details)

    return items


def _build_operation_items(
    results: tuple[HookOperationResult, ...],
    *,
    repo_root: Path,
) -> list[OutputItem]:
    """Build section items for hook operation results."""
    if not results:
        return [raw_item("No managed hooks were processed")]

    items: list[OutputItem] = []

    for result in results:
        items.extend(
            [
                field_item("hook", result.name.value),
                field_item("status", result.after_status.value),
                field_item("path", _display_path(result.path, repo_root)),
                field_item("action", result.action.value),
                field_item("changed", "yes" if result.changed else "no"),
            ]
        )

        if result.before_status != HookStatus.UNSUPPORTED:
            items.append(field_item("managed", "yes" if result.managed else "no"))

        if result.details:
            items.extend(bullet_item(detail) for detail in result.details)

    return items


def build_hooks_status_output(
    report: HooksStatusReport,
    *,
    repo_root: Path,
) -> CommandOutput:
    """Build one unified output model for ``hooks status``."""
    ok = report.overall_status == HooksStatusLevel.HEALTHY
    message = (
        success_message("Managed hooks are healthy")
        if ok
        else warning_message("Managed hooks need attention")
    )

    sections = [
        section(
            "Hooks status",
            field_item("hooks_path", path_to_str(report.hooks_path)),
            field_item("overall_status", report.overall_status.value),
            *(bullet_item(detail) for detail in report.details),
        ),
        section(
            "Hooks",
            *_build_inspection_items(report.results, repo_root=repo_root),
        ),
    ]

    return CommandOutput(
        messages=[message],
        sections=sections,
        metadata={
            "kind": "hooks_status",
            "hooks_path": path_to_str(report.hooks_path),
            "overall_status": report.overall_status.value,
            "details": list(report.details),
            "results": [_build_hook_inspection_payload(result) for result in report.results],
            "ok": ok,
        },
    )


def build_hook_operation_output(
    report: HookOperationReport,
    *,
    repo_root: Path,
    operation_name: str,
) -> CommandOutput:
    """Build one unified output model for a managed hook operation."""
    if report.final_status == HooksStatusLevel.CONFLICT:
        message = warning_message(f"Managed hooks {operation_name} finished with conflicts")
        ok = False
    elif report.changed:
        message = success_message(f"Managed hooks {operation_name} completed")
        ok = True
    else:
        message = warning_message(f"Managed hooks {operation_name} made no changes")
        ok = True

    sections = [
        section(
            "Hooks operation",
            field_item("hooks_path", path_to_str(report.hooks_path)),
            field_item("final_status", report.final_status.value),
            field_item("changed", "yes" if report.changed else "no"),
            *(bullet_item(detail) for detail in report.details),
        ),
        section(
            "Hooks",
            *_build_operation_items(report.results, repo_root=repo_root),
        ),
    ]

    return CommandOutput(
        messages=[message],
        sections=sections,
        metadata={
            "kind": "hooks_operation",
            "operation_name": operation_name,
            "hooks_path": path_to_str(report.hooks_path),
            "overall_status": report.final_status.value,
            "changed": report.changed,
            "details": list(report.details),
            "results": [_build_hook_operation_payload(result) for result in report.results],
            "ok": ok,
        },
    )
