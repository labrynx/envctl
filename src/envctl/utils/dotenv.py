"""Helpers for reading and writing dotenv-style files."""

from __future__ import annotations

from pathlib import Path


def parse_env_text(content: str) -> dict[str, str]:
    """Parse a dotenv-like text payload into a mapping."""
    result: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and (
            (value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))
        ):
            value = value[1:-1]
        result[key] = value
    return result


def load_env_file(path: Path) -> dict[str, str]:
    """Load a dotenv file when present."""
    if not path.exists():
        return {}
    return parse_env_text(path.read_text(encoding="utf-8"))


def _needs_quotes(value: str) -> bool:
    """Return whether a dotenv value should be quoted."""
    if value == "":
        return True

    special_chars = {" ", "\t", "\n", "\r", "#", '"', "'"}
    return any(char in value for char in special_chars)


def _dump_env_value(value: str) -> str:
    """Serialize one dotenv value."""
    if not _needs_quotes(value):
        return value

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dump_env(data: dict[str, str], header: str | None = None) -> str:
    """Dump a mapping to dotenv text."""
    lines: list[str] = []
    if header:
        lines.append(header.rstrip("\n"))
        lines.append("")

    for key in sorted(data):
        value = data[key]
        lines.append(f"{key}={_dump_env_value(value)}")

    lines.append("")
    return "\n".join(lines)
