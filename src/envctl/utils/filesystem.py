"""Generic filesystem helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def ensure_file(path: Path, content: str = "") -> None:
    """Create a file if it does not exist."""
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def is_empty_dir(path: Path) -> bool:
    """Return whether a directory exists and is empty."""
    if not path.exists() or not path.is_dir():
        return False
    return not any(path.iterdir())
