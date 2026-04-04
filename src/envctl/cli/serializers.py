"""JSON serializers for CLI output."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import typer

from envctl.domain.doctor import DoctorCheck
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.domain.status import StatusReport
from envctl.services.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ErrorDiagnostics,
    ProjectBindingDiagnostics,
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)
from envctl.utils.masking import mask_value


def emit_json(payload: Mapping[str, Any]) -> None:
    """Emit one structured JSON payload to stdout."""
    typer.echo(json.dumps(dict(payload), indent=2, sort_keys=True))


def _path_to_str(path: Path) -> str:
    """Serialize one path to string."""
    return str(path)


def serialize_project_context(context: ProjectContext) -> dict[str, Any]:
    """Serialize one project context."""
    return {
        "project_slug": context.project_slug,
        "project_key": context.project_key,
        "project_id": context.project_id,
        "display_name": context.display_name,
        "repo_root": _path_to_str(context.repo_root),
        "repo_remote": context.repo_remote,
        "binding_source": context.binding_source,
        "repo_env_path": _path_to_str(context.repo_env_path),
        "repo_contract_path": _path_to_str(context.repo_contract_path),
        "vault_project_dir": _path_to_str(context.vault_project_dir),
        "vault_values_path": _path_to_str(context.vault_values_path),
        "vault_state_path": _path_to_str(context.vault_state_path),
    }


def serialize_resolved_value(item: ResolvedValue) -> dict[str, Any]:
    """Serialize one resolved value."""
    shown_raw_value = None if item.raw_value is None or item.masked else item.raw_value
    shown_value = mask_value(item.value) if item.masked else item.value
    return {
        "key": item.key,
        "raw_value": shown_raw_value,
        "value": shown_value,
        "source": item.source,
        "masked": item.masked,
        "expansion_status": item.expansion_status,
        "expansion_refs": list(item.expansion_refs),
        "expansion_error": (
            {
                "kind": item.expansion_error.kind,
                "detail": item.expansion_error.detail,
            }
            if item.expansion_error is not None
            else None
        ),
        "valid": item.valid,
        "detail": item.detail,
    }


def serialize_resolution_report(report: ResolutionReport) -> dict[str, Any]:
    """Serialize one resolution report."""
    return {
        "is_valid": report.is_valid,
        "values": {
            key: serialize_resolved_value(report.values[key]) for key in sorted(report.values)
        },
        "missing_required": list(report.missing_required),
        "unknown_keys": list(report.unknown_keys),
        "invalid_keys": list(report.invalid_keys),
    }


def serialize_status_report(report: StatusReport) -> dict[str, Any]:
    """Serialize one status report."""
    return {
        "project_slug": report.project_slug,
        "project_id": report.project_id,
        "repo_root": _path_to_str(report.repo_root),
        "contract_exists": report.contract_exists,
        "vault_exists": report.vault_exists,
        "resolved_valid": report.resolved_valid,
        "summary": report.summary,
        "issues": list(report.issues),
        "suggested_action": report.suggested_action,
    }


def serialize_projection_validation_diagnostics(
    diagnostics: ProjectionValidationDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one blocked projection command."""
    return {
        "operation": diagnostics.operation,
        "active_profile": diagnostics.active_profile,
        "selected_group": diagnostics.selected_group,
        "report": serialize_resolution_report(diagnostics.report),
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_contract_diagnostics(
    diagnostics: ContractDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one contract failure."""
    return {
        "category": diagnostics.category,
        "path": _path_to_str(diagnostics.path),
        "key": diagnostics.key,
        "field": diagnostics.field,
        "issues": [
            {
                "field": issue.field,
                "detail": issue.detail,
            }
            for issue in diagnostics.issues
        ],
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_config_diagnostics(
    diagnostics: ConfigDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one configuration failure."""
    return {
        "category": diagnostics.category,
        "path": _path_to_str(diagnostics.path) if diagnostics.path is not None else None,
        "key": diagnostics.key,
        "field": diagnostics.field,
        "source_label": diagnostics.source_label,
        "value": diagnostics.value,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_state_diagnostics(
    diagnostics: StateDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one state failure."""
    return {
        "category": diagnostics.category,
        "path": _path_to_str(diagnostics.path),
        "field": diagnostics.field,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_repository_discovery_diagnostics(
    diagnostics: RepositoryDiscoveryDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for repository discovery failures."""
    return {
        "category": diagnostics.category,
        "repo_root": _path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "cwd": _path_to_str(diagnostics.cwd) if diagnostics.cwd else None,
        "git_args": list(diagnostics.git_args),
        "git_stdout": diagnostics.git_stdout,
        "git_stderr": diagnostics.git_stderr,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_project_binding_diagnostics(
    diagnostics: ProjectBindingDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for project binding failures."""
    return {
        "category": diagnostics.category,
        "repo_root": _path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "project_id": diagnostics.project_id,
        "matching_ids": list(diagnostics.matching_ids),
        "matching_directories": [_path_to_str(path) for path in diagnostics.matching_directories],
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_error_diagnostics(diagnostics: ErrorDiagnostics) -> dict[str, Any]:
    """Serialize one known structured error diagnostics payload."""
    if isinstance(diagnostics, ProjectionValidationDiagnostics):
        return serialize_projection_validation_diagnostics(diagnostics)
    if isinstance(diagnostics, ContractDiagnostics):
        return serialize_contract_diagnostics(diagnostics)
    if isinstance(diagnostics, ConfigDiagnostics):
        return serialize_config_diagnostics(diagnostics)
    if isinstance(diagnostics, StateDiagnostics):
        return serialize_state_diagnostics(diagnostics)
    if isinstance(diagnostics, RepositoryDiscoveryDiagnostics):
        return serialize_repository_discovery_diagnostics(diagnostics)
    if isinstance(diagnostics, ProjectBindingDiagnostics):
        return serialize_project_binding_diagnostics(diagnostics)

    raise TypeError(f"Unsupported diagnostics type: {type(diagnostics).__name__}")


def serialize_doctor_checks(checks: Iterable[DoctorCheck]) -> dict[str, Any]:
    """Serialize doctor checks and aggregate their summary."""
    items = list(checks)
    has_failures = any(check.status == "fail" for check in items)

    return {
        "has_failures": has_failures,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "detail": check.detail,
            }
            for check in items
        ],
    }


def serialize_error(
    *,
    error_type: str,
    message: str,
    command: str | None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Serialize one command error."""
    error_payload: dict[str, Any] = {
        "type": error_type,
        "message": message,
    }
    if details is not None:
        error_payload["details"] = dict(details)

    payload: dict[str, Any] = {
        "ok": False,
        "command": command,
        "error": error_payload,
    }
    return payload
