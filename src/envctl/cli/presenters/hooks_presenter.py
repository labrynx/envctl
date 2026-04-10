"""Presenters for managed hooks commands."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.hooks import (
    HookInspectionResult,
    HookOperationReport,
    HookOperationResult,
    HooksStatusLevel,
    HooksStatusReport,
    HookStatus,
)
from envctl.utils.output import print_kv, print_section, print_success, print_warning


def render_hooks_status(report: HooksStatusReport, *, repo_root: Path) -> None:
    """Render managed hooks status in human-readable text."""
    if report.overall_status == HooksStatusLevel.HEALTHY:
        print_success("Managed hooks are healthy")
    else:
        print_warning("Managed hooks need attention")
    print_kv("hooks_path", str(report.hooks_path))
    print_kv("overall_status", report.overall_status.value)
    _render_report_details(report.details)
    _render_inspection_results(report.results, repo_root=repo_root)


def render_hook_operation(
    report: HookOperationReport,
    *,
    repo_root: Path,
    operation_name: str,
) -> None:
    """Render one managed hook operation result."""
    if report.final_status == HooksStatusLevel.CONFLICT:
        print_warning(f"Managed hooks {operation_name} finished with conflicts")
    elif report.changed:
        print_success(f"Managed hooks {operation_name} completed")
    else:
        print_warning(f"Managed hooks {operation_name} made no changes")
    print_kv("hooks_path", str(report.hooks_path))
    print_kv("final_status", report.final_status.value)
    print_kv("changed", "yes" if report.changed else "no")
    _render_report_details(report.details)
    _render_operation_results(report.results, repo_root=repo_root)


def _render_report_details(details: tuple[str, ...]) -> None:
    for detail in details:
        print_warning(detail)


def _render_inspection_results(
    results: tuple[HookInspectionResult, ...],
    *,
    repo_root: Path,
) -> None:
    print_section("Hooks")
    for result in results:
        print_kv(result.name.value, result.status.value)
        print_kv("path", _display_path(result.path, repo_root))
        print_kv("managed", "yes" if result.managed else "no")
        if result.is_executable is not None:
            print_kv("is_executable", "yes" if result.is_executable else "no")
        for detail in result.details:
            print_warning(detail)


def _render_operation_results(
    results: tuple[HookOperationResult, ...],
    *,
    repo_root: Path,
) -> None:
    print_section("Hooks")
    for result in results:
        print_kv(result.name.value, result.after_status.value)
        print_kv("path", _display_path(result.path, repo_root))
        print_kv("action", result.action.value)
        print_kv("changed", "yes" if result.changed else "no")
        if result.before_status != HookStatus.UNSUPPORTED:
            print_kv("managed", "yes" if result.managed else "no")
        for detail in result.details:
            print_warning(detail)


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)
