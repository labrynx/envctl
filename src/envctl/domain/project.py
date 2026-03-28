"""Project domain models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ConfirmFn = Callable[[str, bool], bool]


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
