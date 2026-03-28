"""Helpers for simple dotenv-style files."""

from __future__ import annotations

import re
from pathlib import Path

from envctl.errors import ValidationError
from envctl.utils.atomic import write_text_atomic

ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def normalize_env_key(key: str) -> str:
    """Normalize and validate an environment variable key."""
    normalized_key = key.strip()

    if not normalized_key:
        raise ValidationError("Key cannot be empty")

    if not ENV_KEY_PATTERN.match(normalized_key):
        raise ValidationError(
            "Key must start with a letter or underscore "
            "and contain only letters, digits, or underscores"
        )

    return normalized_key


def validate_env_value(value: str) -> None:
    """Validate a simple dotenv value."""
    if "\n" in value or "\r" in value:
        raise ValidationError("Value cannot contain newlines")


def update_env_file_key(path: Path, key: str, value: str) -> None:
    """Insert or update a key in a dotenv-style file."""
    lines: list[str] = []
    found = False

    if path.exists():
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

    updated_lines: list[str] = []

    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue

        current_key, _current_value = line.split("=", 1)
        if current_key == key:
            updated_lines.append(f"{key}={value}")
            found = True
        else:
            updated_lines.append(line)

    if not found:
        updated_lines.append(f"{key}={value}")

    final_content = "\n".join(updated_lines).rstrip("\n") + "\n"
    write_text_atomic(path, final_content)
