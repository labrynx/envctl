"""Repository status domain models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
