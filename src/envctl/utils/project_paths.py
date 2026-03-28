"""Project path helpers."""

from __future__ import annotations

from pathlib import Path


def build_vault_project_dir(project_slug: str, project_id: str, projects_dir: Path) -> Path:
    """Return the vault directory for a project."""
    return projects_dir / f"{project_slug}--{project_id}"
