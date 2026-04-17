"""Structured payload builders for presenter metadata."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning, DiagnosticSummary
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.domain.selection import ContractSelection
from envctl.utils.masking import mask_value


def path_to_str(path: str | Path) -> str:
    """Serialize one path using stable POSIX-like separators."""
    return str(path).replace("\\", "/")


def optional_path_to_str(path: str | Path | None) -> str | None:
    """Serialize one optional path to string."""
    return None if path is None else path_to_str(path)


def _build_expansion_error_payload(item: ResolvedValue) -> dict[str, Any] | None:
    """Serialize one resolved value expansion error."""
    if item.expansion_error is None:
        return None

    return {
        "kind": item.expansion_error.kind,
        "detail": item.expansion_error.detail,
    }


def _build_visible_raw_value(item: ResolvedValue) -> str | None:
    """Return the visible raw value for one resolved value."""
    if item.raw_value is None or item.masked:
        return None
    return item.raw_value


def _build_visible_value(item: ResolvedValue) -> str:
    """Return the visible value for one resolved value."""
    return mask_value(item.value) if item.masked else item.value


def build_resolution_problem_lines(
    report: ResolutionReport,
    *,
    unknown_keys_title: str = "Unknown keys in vault",
) -> list[str]:
    """Build actionable problem lines for one resolution report."""
    lines: list[str] = []

    def append_group(title: str, entries: list[str]) -> None:
        if not entries:
            return
        lines.extend(("", title, *entries))

    append_group(
        "Missing required keys",
        [f"  - {key}" for key in report.missing_required],
    )

    invalid_entries: list[str] = []
    for key in report.invalid_keys:
        item = report.values.get(key)
        if item is not None and item.detail:
            invalid_entries.append(f"  - {key}: {item.detail}")
        else:
            invalid_entries.append(f"  - {key}")

    append_group("Invalid keys", invalid_entries)

    append_group(
        unknown_keys_title,
        [f"  - {key}" for key in report.unknown_keys],
    )

    return lines


def build_project_context_payload(context: ProjectContext) -> dict[str, Any]:
    """Serialize one project context."""
    return {
        "project_slug": context.project_slug,
        "project_key": context.project_key,
        "project_id": context.project_id,
        "display_name": context.display_name,
        "repo_root": path_to_str(context.repo_root),
        "repo_remote": context.repo_remote,
        "binding_source": context.binding_source,
        "repo_env_path": path_to_str(context.repo_env_path),
        "repo_contract_path": path_to_str(context.repo_contract_path),
        "vault_project_dir": path_to_str(context.vault_project_dir),
        "vault_values_path": path_to_str(context.vault_values_path),
        "vault_state_path": path_to_str(context.vault_state_path),
    }


def build_resolved_value_payload(item: ResolvedValue) -> dict[str, Any]:
    """Serialize one resolved value."""
    return {
        "key": item.key,
        "raw_value": _build_visible_raw_value(item),
        "value": _build_visible_value(item),
        "source": item.source,
        "masked": item.masked,
        "expansion_status": item.expansion_status,
        "expansion_refs": list(item.expansion_refs),
        "expansion_error": _build_expansion_error_payload(item),
        "valid": item.valid,
        "detail": item.detail,
    }


def build_diagnostic_summary_payload(summary: DiagnosticSummary) -> dict[str, int]:
    """Serialize one diagnostic summary."""
    return {
        "total": summary.total,
        "valid": summary.valid,
        "invalid": summary.invalid,
        "unknown": summary.unknown,
    }


def build_command_warning_payload(warning: CommandWarning) -> dict[str, str]:
    """Serialize one command warning."""
    return {
        "kind": warning.kind,
        "message": warning.message,
    }


def serialize_contract_deprecation_warnings(
    warnings: Sequence[ContractDeprecationWarning],
) -> list[dict[str, Any]]:
    """Serialize contract deprecation warnings."""
    return [
        {
            "kind": "contract_deprecation",
            "key": warning.key,
            "deprecated_field": warning.deprecated_field,
            "message": warning.message,
        }
        for warning in warnings
    ]


def serialize_command_warnings(
    warnings: Sequence[CommandWarning],
) -> list[dict[str, Any]]:
    """Serialize command warnings."""
    return [
        {
            "kind": warning.kind,
            "message": warning.message,
        }
        for warning in warnings
    ]


def build_command_warnings_payload(
    *,
    contract_warnings: Sequence[ContractDeprecationWarning] = (),
    command_warnings: Sequence[CommandWarning] = (),
    extra_warnings: Sequence[CommandWarning] = (),
) -> list[dict[str, Any]]:
    """Serialize all CLI-visible warnings in a stable order."""
    return (
        serialize_contract_deprecation_warnings(contract_warnings)
        + serialize_command_warnings(command_warnings)
        + serialize_command_warnings(extra_warnings)
    )


def build_resolution_report_payload(report: ResolutionReport) -> dict[str, Any]:
    """Serialize one resolution report."""
    return {
        "is_valid": report.is_valid,
        "values": {
            key: build_resolved_value_payload(report.values[key]) for key in sorted(report.values)
        },
        "missing_required": list(report.missing_required),
        "unknown_keys": list(report.unknown_keys),
        "invalid_keys": list(report.invalid_keys),
    }


def build_contract_selection_payload(selection: ContractSelection) -> dict[str, Any]:
    """Serialize one normalized selection scope."""
    return {
        "mode": selection.mode,
        "group": selection.group,
        "set": selection.set_name,
        "var": selection.variable,
    }
