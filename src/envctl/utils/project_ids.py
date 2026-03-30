"""Project identifier helpers."""

from __future__ import annotations

import re
import secrets

from envctl.constants import PROJECT_ID_HEX_LENGTH, PROJECT_ID_PREFIX

_PROJECT_ID_RE = re.compile(rf"^{re.escape(PROJECT_ID_PREFIX)}[0-9a-f]{{{PROJECT_ID_HEX_LENGTH}}}$")


def new_project_id() -> str:
    """Return a new canonical project id."""
    return f"{PROJECT_ID_PREFIX}{secrets.token_hex(PROJECT_ID_HEX_LENGTH // 2)}"


def is_valid_project_id(value: str) -> bool:
    """Return whether a value is a canonical project id."""
    return bool(_PROJECT_ID_RE.fullmatch(value))
