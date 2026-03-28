"""Repository metadata domain model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectMetadata:
    """Persisted repository metadata linking repo and vault."""

    version: int
    project_slug: str
    project_id: str
    env_filename: str
    vault_project_dir: Path
    vault_env_path: Path
    repo_fingerprint: str
