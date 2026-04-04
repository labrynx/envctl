"""Error envelope serializers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def serialize_error(
    *,
    error_type: str,
    message: str,
    command: str | None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Serialize one command error."""
    error_payload: dict[str, Any] = {
        "type": error_type,
        "message": message,
    }
    if details is not None:
        error_payload["details"] = dict(details)

    return {
        "ok": False,
        "command": command,
        "error": error_payload,
    }
