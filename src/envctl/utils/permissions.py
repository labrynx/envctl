"""Permission helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_private_dir_permissions(path: Path) -> None:
    """Try to apply user-only permissions to a directory."""
    try:
        path.chmod(0o700)
    except OSError:
        return None


def ensure_private_file_permissions(path: Path) -> None:
    """Try to apply user-only permissions to a file."""
    try:
        path.chmod(0o600)
    except OSError:
        return None
