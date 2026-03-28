"""Shell output helpers."""

from __future__ import annotations

import shlex


def to_export_lines(data: dict[str, str]) -> str:
    """Render shell export lines."""
    lines = [f"export {key}={shlex.quote(value)}" for key, value in sorted(data.items())]
    return "\n".join(lines) + "\n"
