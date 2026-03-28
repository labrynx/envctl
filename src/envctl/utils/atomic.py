"""Atomic file writing helpers."""

from __future__ import annotations

import json
from pathlib import Path


def write_text_atomic(path: Path, content: str) -> None:
    """Write text to a file atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def write_json_atomic(path: Path, payload: dict) -> None:
    """Write JSON to a file atomically."""
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    write_text_atomic(path, content)
