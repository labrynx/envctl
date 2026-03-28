"""Shell output helpers."""

from __future__ import annotations


def shell_single_quote(value: str) -> str:
    """Return a POSIX-safe single-quoted shell string."""
    return "'" + value.replace("'", "'\"'\"'") + "'"


def to_shell_export_line(key: str, value: str) -> str:
    """Render one environment variable as a shell export line."""
    return f"export {key}={shell_single_quote(value)}"


def to_shell_export_lines(values: dict[str, str]) -> list[str]:
    """Render environment values as POSIX shell export lines."""
    return [to_shell_export_line(key, value) for key, value in values.items()]
