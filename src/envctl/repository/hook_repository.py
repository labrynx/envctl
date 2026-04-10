"""Filesystem access for managed Git hooks."""

from __future__ import annotations

import os
from pathlib import Path

from envctl.utils.atomic import write_text_atomic


class HookRepository:
    """Thin filesystem abstraction for managed hook files."""

    def read(self, path: Path) -> str:
        """Read one hook file with normalized line endings."""
        content = path.read_text(encoding="utf-8")
        return content.replace("\r\n", "\n").replace("\r", "\n")

    def write(self, path: Path, content: str) -> None:
        """Write one hook file atomically using LF line endings."""
        write_text_atomic(path, content, mode=0o644)

    def exists(self, path: Path) -> bool:
        """Return whether one hook file exists."""
        return path.exists()

    def remove(self, path: Path) -> None:
        """Remove one hook file when present."""
        path.unlink(missing_ok=True)

    def is_executable(self, path: Path) -> bool | None:
        """Return whether one hook file is executable on platforms that support it."""
        if self._is_windows():
            return None
        return os.access(path, os.X_OK)

    def ensure_executable(self, path: Path) -> None:
        """Ensure one hook file is executable when the platform supports it."""
        if self._is_windows():
            return
        current_mode = path.stat().st_mode
        path.chmod(current_mode | 0o111)

    def _is_windows(self) -> bool:
        return os.name == "nt"
