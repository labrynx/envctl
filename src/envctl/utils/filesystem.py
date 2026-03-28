"""Filesystem helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create a directory if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_file(path: Path, content: str = "") -> Path:
    """Create a file if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")
    return path


def is_world_writable(path: Path) -> bool:
    """Return whether the path is world-writable when POSIX permissions are available."""
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return bool(mode & 0o002)
