"""Helpers for project naming."""

from __future__ import annotations

import re
from pathlib import Path

from envctl.errors import ProjectDetectionError


def slugify_project_name(name: str) -> str:
    """Normalize a project name into a filesystem-safe slug."""
    value = name.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")

    if not value:
        raise ProjectDetectionError("Project name resolved to empty value")

    return value


def resolve_project_name(repo_root: Path, explicit_project_name: str | None) -> str:
    """Resolve the effective project slug."""
    if explicit_project_name:
        return slugify_project_name(explicit_project_name)
    return slugify_project_name(repo_root.name)
