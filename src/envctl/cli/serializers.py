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
) -> dict[str, Any]:
    """Serialize one command error."""
    return {
        "ok": False,
        "command": command,
        "error": {
            "type": error_type,
            "message": message,
        },
    }
