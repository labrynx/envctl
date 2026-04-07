from __future__ import annotations

from pathlib import Path


def normalize_path_str(value: str | Path) -> str:
    """Return a stable POSIX-like string for path assertions."""
    return str(value).replace("\\", "/")
