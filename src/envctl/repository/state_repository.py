"""State persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path

from envctl.constants import STATE_VERSION
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


def read_state(path: Path) -> dict | None:
    """Read state when present."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
