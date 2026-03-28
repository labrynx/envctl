"""Persistence helpers for repository metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envctl.constants import METADATA_VERSION
from envctl.domain.metadata import ProjectMetadata
from envctl.utils.atomic import write_json_atomic


def write_project_metadata(
    path: Path,
    *,
    project_slug: str,
    project_id: str,
    env_filename: str,
    vault_project_dir: Path,
    vault_env_path: Path,
    repo_fingerprint: str,
) -> None:
    """Write repository metadata for a managed envctl project."""
    write_json_atomic(
        path,
        {
            "version": METADATA_VERSION,
            "project_slug": project_slug,
            "project_id": project_id,
            "env_filename": env_filename,
            "vault_project_dir": str(vault_project_dir),
            "vault_env_path": str(vault_env_path),
            "repo_fingerprint": repo_fingerprint,
        },
    )


def read_project_metadata_record(path: Path) -> dict[str, Any] | None:
    """Read repository metadata and return the raw mapping when valid."""
    if not path.exists():
        return None

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(raw, dict):
        return None

    return raw


def read_project_metadata(path: Path) -> ProjectMetadata | None:
    """Read repository metadata and return a typed model when valid."""
    raw = read_project_metadata_record(path)
    if raw is None:
        return None

    version = raw.get("version")
    project_slug = raw.get("project_slug")
    project_id = raw.get("project_id")
    env_filename = raw.get("env_filename")
    vault_project_dir = raw.get("vault_project_dir")
    vault_env_path = raw.get("vault_env_path")
    repo_fingerprint = raw.get("repo_fingerprint")

    if not isinstance(version, int):
        return None
    if not isinstance(project_slug, str) or not project_slug.strip():
        return None
    if not isinstance(project_id, str) or not project_id.strip():
        return None
    if not isinstance(env_filename, str) or not env_filename.strip():
        return None
    if not isinstance(vault_project_dir, str) or not vault_project_dir.strip():
        return None
    if not isinstance(vault_env_path, str) or not vault_env_path.strip():
        return None
    if not isinstance(repo_fingerprint, str) or not repo_fingerprint.strip():
        return None

    return ProjectMetadata(
        version=version,
        project_slug=project_slug.strip(),
        project_id=project_id.strip(),
        env_filename=env_filename.strip(),
        vault_project_dir=Path(vault_project_dir).expanduser(),
        vault_env_path=Path(vault_env_path).expanduser(),
        repo_fingerprint=repo_fingerprint.strip(),
    )
