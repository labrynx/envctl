"""Filesystem helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from envctl.constants import METADATA_VERSION


def ensure_dir(path: Path) -> None:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def ensure_file(path: Path, content: str = "") -> None:
    """Create a file if it does not exist."""
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_text_atomic(path: Path, content: str) -> None:
    """Atomically write text content to a file."""
    ensure_dir(path.parent)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temp_name = handle.name

    os.replace(temp_name, path)


def write_json_atomic(path: Path, data: dict[str, object]) -> None:
    """Atomically write JSON content to a file."""
    write_text_atomic(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


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
    """Write repository metadata for a managed envctl project.

    TODO(v1.1):
    - store optional remote URL details separately for easier diagnostics
    - store initialization timestamp and last-validation timestamp
    - support future migration metadata when new flags/config formats arrive
    """
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


def read_project_metadata(path: Path) -> str | None:
    """Read repository metadata and return the stored project slug.

    This keeps compatibility with older code paths while metadata evolves.
    """
    record = read_project_metadata_record(path)
    if not record:
        return None

    candidates = [
        record.get("project_slug"),
        record.get("project"),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def update_env_file_key(path: Path, key: str, value: str) -> None:
    """Insert or update a key in a dotenv-style file."""
    lines: list[str] = []
    found = False

    if path.exists():
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

    updated_lines: list[str] = []
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue

        current_key, _current_value = line.split("=", 1)
        if current_key == key:
            updated_lines.append(f"{key}={value}")
            found = True
        else:
            updated_lines.append(line)

    if not found:
        updated_lines.append(f"{key}={value}")

    final_content = "\n".join(updated_lines).rstrip("\n") + "\n"
    write_text_atomic(path, final_content)
