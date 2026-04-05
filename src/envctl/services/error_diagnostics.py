# src/envctl/services/error_diagnostics.py
"""Typed diagnostics for structured CLI-facing errors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from envctl.domain.resolution import ResolutionReport

ProjectionOperation = Literal["run", "sync", "export"]
ContractDiagnosticCategory = Literal[
    "missing_contract_file",
    "invalid_yaml",
    "unreadable_contract",
    "invalid_top_level_shape",
    "invalid_variable_shape",
    "validation_failed",
]
ConfigDiagnosticCategory = Literal[
    "invalid_json",
    "unreadable_config",
    "invalid_config_shape",
    "unsupported_keys",
    "invalid_runtime_mode",
    "invalid_filename",
    "invalid_default_profile",
    "config_file_exists",
]
StateDiagnosticCategory = Literal[
    "corrupted_state",
    "unreadable_state",
    "invalid_state_shape",
    "unsupported_state_version",
    "missing_required_field",
    "invalid_known_paths",
    "non_canonical_project_id",
]
RepositoryDiscoveryDiagnosticCategory = Literal[
    "git_not_installed",
    "not_a_git_repository",
    "git_command_failed",
]
ProjectBindingDiagnosticCategory = Literal[
    "multiple_vault_directories",
    "ambiguous_vault_identity",
    "invalid_bound_project_id",
    "bound_project_missing_vault",
]


@dataclass(frozen=True)
class ContractDiagnosticIssue:
    """One structured contract validation issue."""

    field: str
    detail: str


@dataclass(frozen=True)
class ProjectionValidationDiagnostics:
    """Structured diagnostics for projection-blocked operations."""

    operation: ProjectionOperation
    active_profile: str
    selected_group: str | None
    report: ResolutionReport
    suggested_actions: tuple[str, ...]


@dataclass(frozen=True)
class ContractDiagnostics:
    """Structured diagnostics for contract loading and validation failures."""

    category: ContractDiagnosticCategory
    path: Path
    key: str | None = None
    field: str | None = None
    issues: tuple[ContractDiagnosticIssue, ...] = ()
    suggested_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConfigDiagnostics:
    """Structured diagnostics for configuration failures."""

    category: ConfigDiagnosticCategory
    path: Path | None = None
    key: str | None = None
    field: str | None = None
    source_label: str | None = None
    value: str | None = None
    suggested_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class StateDiagnostics:
    """Structured diagnostics for persisted state failures."""

    category: StateDiagnosticCategory
    path: Path
    field: str | None = None
    suggested_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepositoryDiscoveryDiagnostics:
    """Structured diagnostics for repository discovery failures."""

    category: RepositoryDiscoveryDiagnosticCategory
    repo_root: Path | None = None
    cwd: Path | None = None
    git_args: tuple[str, ...] = ()
    git_stdout: str | None = None
    git_stderr: str | None = None
    suggested_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProjectBindingDiagnostics:
    """Structured diagnostics for binding and identity failures."""

    category: ProjectBindingDiagnosticCategory
    repo_root: Path | None = None
    project_id: str | None = None
    matching_ids: tuple[str, ...] = ()
    matching_directories: tuple[Path, ...] = ()
    suggested_actions: tuple[str, ...] = ()


ErrorDiagnostics = (
    ProjectionValidationDiagnostics
    | ContractDiagnostics
    | ConfigDiagnostics
    | StateDiagnostics
    | RepositoryDiscoveryDiagnostics
    | ProjectBindingDiagnostics
)
