"""Permission helpers."""

from __future__ import annotations

import os
from pathlib import Path


def ensure_private_file_permissions(path: Path) -> None:
    """Restrict a file to user-only permissions when the platform allows it."""
    try:
        os.chmod(path, 0o600)
    except OSError:
        return


def ensure_private_dir_permissions(path: Path) -> None:
    """Restrict a directory to user-only permissions when the platform allows it."""
    try:
        os.chmod(path, 0o700)
    except OSError:
        return


def is_path_world_writable(path: Path) -> bool:
    """Return whether a path exists and is world-writable."""
    if not path.exists():
        return False

    mode = path.stat().st_mode
    return bool(mode & 0o002)
