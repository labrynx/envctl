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


def _migrate_state_v1_to_v2(raw: dict[str, Any]) -> dict[str, Any]:
    """Upgrade a v1 state payload to the v2 shape in memory."""
    now = _utc_now_iso()

    project_slug = raw.get("project_slug")
    project_id = raw.get("project_id")
    repo_root = raw.get("repo_root")

    known_paths = raw.get("known_paths")
    if known_paths is None:
        known_paths = []
    if not isinstance(known_paths, list):
        known_paths = []

    normalized_known_paths = [
        item for item in known_paths if isinstance(item, str) and item.strip()
    ]

    if isinstance(repo_root, str) and repo_root.strip() and repo_root not in normalized_known_paths:
        normalized_known_paths.append(repo_root)

    return {
        "version": STATE_VERSION,
        "project_slug": project_slug,
        "project_key": raw.get("project_key") or project_slug,
        "project_id": project_id,
        "repo_root": repo_root,
        "git_remote": raw.get("git_remote"),
        "known_paths": normalized_known_paths,
        "created_at": raw.get("created_at") or now,
        "last_seen_at": raw.get("last_seen_at") or now,
    }


def _normalize_state_payload(raw: dict[str, Any], path: Path) -> dict[str, Any]:
    """Normalize supported state versions to the current shape."""
    version = raw.get("version")

    if version == STATE_VERSION:
        return raw

    if version == 1:
        return _migrate_state_v1_to_v2(raw)

    raise StateError(f"Unsupported state version in {path}: {version}")


def _validate_state_payload(raw: dict[str, Any], path: Path) -> dict[str, Any]:
    """Validate the normalized state payload."""
    project_id = raw.get("project_id")
    project_slug = raw.get("project_slug")
    project_key = raw.get("project_key")
    repo_root = raw.get("repo_root")
    known_paths = raw.get("known_paths", [])

    if not isinstance(project_id, str) or not project_id.strip():
        raise StateError(f"State file is missing a valid project_id: {path}")

    if not isinstance(project_slug, str) or not project_slug.strip():
        raise StateError(f"State file is missing a valid project_slug: {path}")

    if not isinstance(project_key, str) or not project_key.strip():
        raise StateError(f"State file is missing a valid project_key: {path}")

    if not isinstance(repo_root, str) or not repo_root.strip():
        raise StateError(f"State file is missing a valid repo_root: {path}")

    if known_paths is None:
        known_paths = []

    if not isinstance(known_paths, list) or not all(isinstance(item, str) for item in known_paths):
        raise StateError(f"State file has invalid known_paths: {path}")

    raw["known_paths"] = known_paths
    raw["version"] = STATE_VERSION
    return raw


def read_state(path: Path) -> dict[str, Any] | None:
    """Read state when present.

    Missing state is normal.
    Corrupt or unreadable state is an explicit error.
    Supported legacy versions are normalized in memory.
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

    normalized = _normalize_state_payload(raw, path)
    return _validate_state_payload(normalized, path)


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
    now = _utc_now_iso()
    write_json_atomic(
        path,
        {
            "version": STATE_VERSION,
            "project_slug": project_slug,
            "project_key": project_slug,
            "project_id": project_id,
            "repo_root": repo_root,
            "git_remote": None,
            "known_paths": [repo_root],
            "created_at": now,
            "last_seen_at": now,
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
