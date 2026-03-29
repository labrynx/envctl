"""Filesystem helpers."""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path


def ensure_dir(path: Path, *, mode: int = 0o700) -> Path:
    """Create a directory if needed."""
    path.mkdir(parents=True, exist_ok=True)
    with suppress(OSError):
        path.chmod(mode)
    return path


def ensure_file(path: Path, content: str = "", *, mode: int = 0o600) -> Path:
    """Create a file if it does not exist using restrictive permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(path, flags, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    else:
        with suppress(OSError):
            path.chmod(mode)
    return path


def is_world_writable(path: Path) -> bool:
    """Return whether the path is world-writable when POSIX permissions are available."""
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return bool(mode & 0o002)
