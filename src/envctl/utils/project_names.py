"""Project naming helpers."""

from __future__ import annotations

import re
from pathlib import Path


def slugify_project_name(value: str) -> str:
    """Convert a project name into a filesystem-safe slug."""
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered)
    lowered = lowered.strip("-")
    return lowered or "project"


def resolve_project_name(repo_root: Path, explicit_name: str | None) -> str:
    """Resolve the final project slug."""
    if explicit_name and explicit_name.strip():
        return slugify_project_name(explicit_name)
    return slugify_project_name(repo_root.name)
