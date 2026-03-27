"""Domain models used across services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Resolved application configuration."""

    config_path: Path
    vault_dir: Path
    env_filename: str
    metadata_filename: str

    @property
    def projects_dir(self) -> Path:
        return self.vault_dir / "projects"


@dataclass(frozen=True)
class ProjectContext:
    """Resolved project context for a repository and vault entry."""

    project_slug: str
    project_id: str
    repo_root: Path
    repo_metadata_path: Path
    repo_env_path: Path
    vault_project_dir: Path
    vault_env_path: Path

    @property
    def project_name(self) -> str:
        """Backward-compatible alias for older command output."""
        return self.project_slug


@dataclass(frozen=True)
class StatusReport:
    """Human-oriented repository status report."""

    state: str
    project_slug: str | None
    project_id: str | None
    repo_root: Path
    repo_metadata_path: Path
    repo_env_path: Path
    vault_env_path: Path | None
    summary: str
    repo_env_status: str
    vault_env_status: str
    issues: list[str]
    suggested_action: str | None


@dataclass(frozen=True)
class DoctorCheck:
    """Single doctor check result."""

    name: str
    status: str
    detail: str