"""State persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envctl.constants import STATE_VERSION
from envctl.errors import StateError
from envctl.utils.atomic import write_json_atomic


def write_state(
    path: Path,
    *,
    project_slug: str,
    project_id: str,
    repo_root: str,
) -> None:
    """Write minimal per-project state inside the vault."""
    write_json_atomic(
        path,
        {
            "version": STATE_VERSION,
            "project_slug": project_slug,
            "project_id": project_id,
            "repo_root": repo_root,
        },
    )


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

    return raw
