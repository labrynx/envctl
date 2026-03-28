"""Helpers for displaying user-friendly paths."""

from __future__ import annotations

from pathlib import Path


def to_tilde_path(path: Path) -> str:
    """Return a user-friendly path using `~` when it is inside the home directory."""
    home = Path.home().resolve()
    resolved = path.expanduser().resolve()

    try:
        relative = resolved.relative_to(home)
    except ValueError:
        return str(resolved)

    if not relative.parts:
        return "~"

    return str(Path("~") / relative)
