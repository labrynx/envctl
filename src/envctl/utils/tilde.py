"""Helpers for `~` path rendering."""

from __future__ import annotations

from pathlib import Path


def to_tilde_path(path: Path) -> str:
    """Render a path using `~` when it is inside the user home directory."""
    home = Path.home().resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(home)
    except ValueError:
        return str(resolved)
    return str(Path("~") / relative)
