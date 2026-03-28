"""Permission helpers."""

from __future__ import annotations

import os
from pathlib import Path


def ensure_private_file_permissions(path: Path) -> None:
    """Restrict a file to user-only permissions when the platform allows it.

    The target mode is `0o600`.

    Raises:
        OSError: Never raised intentionally. Permission errors are ignored to keep
            the CLI usable on filesystems without POSIX chmod semantics.
    """
    try:
        os.chmod(path, 0o600)
    except OSError:
        return


def ensure_private_dir_permissions(path: Path) -> None:
    """Restrict a directory to user-only permissions when the platform allows it.

    The target mode is `0o700`.

    Raises:
        OSError: Never raised intentionally. Permission errors are ignored to keep
            the CLI usable on filesystems without POSIX chmod semantics.
    """
    try:
        os.chmod(path, 0o700)
    except OSError:
        return


def is_path_world_writable(path: Path) -> bool:
    """Return whether a path exists and is world-writable.

    Args:
        path: Filesystem path to inspect.

    Returns:
        True when the path exists and has the world-writable bit set.
        False otherwise.
    """
    if not path.exists():
        return False

    mode = path.stat().st_mode
    return bool(mode & 0o002)
