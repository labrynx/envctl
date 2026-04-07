"""Structured diagnostics serializers."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.common import path_to_str
from envctl.cli.serializers.resolution import (
    serialize_contract_selection,
    serialize_resolution_report,
)
from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ErrorDiagnostics,
    ProjectBindingDiagnostics,
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)


def serialize_projection_validation_diagnostics(
    diagnostics: ProjectionValidationDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one blocked projection command."""
    return {
        "operation": diagnostics.operation,
        "active_profile": diagnostics.active_profile,
        "selection": serialize_contract_selection(diagnostics.selection),
        "report": serialize_resolution_report(diagnostics.report),
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_contract_diagnostics(
    diagnostics: ContractDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for one contract failure."""
    return {
        "category": diagnostics.category,
        "path": path_to_str(diagnostics.path),
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
        "path": path_to_str(diagnostics.path) if diagnostics.path is not None else None,
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
        "path": path_to_str(diagnostics.path),
        "field": diagnostics.field,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def serialize_repository_discovery_diagnostics(
    diagnostics: RepositoryDiscoveryDiagnostics,
) -> dict[str, Any]:
    """Serialize structured diagnostics for repository discovery failures."""
    return {
        "category": diagnostics.category,
        "repo_root": path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "cwd": path_to_str(diagnostics.cwd) if diagnostics.cwd else None,
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
        "repo_root": path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "project_id": diagnostics.project_id,
        "matching_ids": list(diagnostics.matching_ids),
        "matching_directories": [path_to_str(path) for path in diagnostics.matching_directories],
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
