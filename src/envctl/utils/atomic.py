"""Atomic file writing helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    tmp_path.replace(path)


def write_json_atomic(path: Path, payload: dict) -> None:
    """Write JSON to a file atomically."""
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    write_text_atomic(path, content)
