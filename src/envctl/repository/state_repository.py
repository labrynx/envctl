"""State persistence helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envctl.constants import STATE_VERSION
from envctl.errors import StateError
from envctl.utils.atomic import write_json_atomic


def _utc_now_iso() -> str:
    """Return a UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_state(path: Path) -> dict[str, Any] | None:
    """Read state when present.

    Missing state is normal.
    Corrupt or unreadable state is an explicit error.
    """
    if not path.exists():
        return None

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(f"State file is corrupted: {path}") from exc
    except OSError as exc:
        raise StateError(f"Unable to read state file: {path}") from exc

    if not isinstance(raw, dict):
        raise StateError(f"State file must contain a JSON object: {path}")

    version = raw.get("version")
    if version != STATE_VERSION:
        raise StateError(f"Unsupported state version in {path}: {version}")

    project_id = raw.get("project_id")
    project_slug = raw.get("project_slug")
    if not isinstance(project_id, str) or not project_id.strip():
        raise StateError(f"State file is missing a valid project_id: {path}")
    if not isinstance(project_slug, str) or not project_slug.strip():
        raise StateError(f"State file is missing a valid project_slug: {path}")

    known_paths = raw.get("known_paths", [])
    if known_paths is None:
        known_paths = []
    if not isinstance(known_paths, list) or not all(isinstance(item, str) for item in known_paths):
        raise StateError(f"State file has invalid known_paths: {path}")

    return raw


def write_state(
    path: Path,
    *,
    project_slug: str,
    project_id: str,
    repo_root: str,
) -> None:
    """Write minimal per-project state inside the vault.

    Backward-compatible helper kept for existing tests and callers.
    """
    write_json_atomic(
        path,
        {
            "version": STATE_VERSION,
            "project_slug": project_slug,
            "project_id": project_id,
            "repo_root": repo_root,
            "known_paths": [repo_root],
            "created_at": _utc_now_iso(),
            "last_seen_at": _utc_now_iso(),
        },
    )


def upsert_state(
    path: Path,
    *,
    project_slug: str,
    project_key: str,
    project_id: str,
    repo_root: str,
    git_remote: str | None,
) -> None:
    """Create or update per-project state inside the vault."""
    existing = read_state(path) if path.exists() else None
    now = _utc_now_iso()

    known_paths: list[str] = []
    if existing is not None:
        for item in existing.get("known_paths", []):
            normalized = str(item).strip()
            if normalized and normalized not in known_paths:
                known_paths.append(normalized)

    normalized_repo_root = str(repo_root).strip()
    if normalized_repo_root and normalized_repo_root not in known_paths:
        known_paths.append(normalized_repo_root)

    payload: dict[str, Any] = {
        "version": STATE_VERSION,
        "project_slug": project_slug,
        "project_key": project_key,
        "project_id": project_id,
        "repo_root": normalized_repo_root,
        "git_remote": git_remote,
        "known_paths": known_paths,
        "created_at": existing.get("created_at", now) if existing is not None else now,
        "last_seen_at": now,
    }

    write_json_atomic(path, payload)
