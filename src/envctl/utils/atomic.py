"""Atomic write helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from envctl.utils.filesystem import ensure_dir


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
