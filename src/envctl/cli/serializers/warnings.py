"""Command warning serializers."""

from __future__ import annotations

from typing import Any

from envctl.domain.diagnostics import CommandWarning


def serialize_command_warnings(
    warnings: tuple[CommandWarning, ...] | list[CommandWarning],
) -> list[dict[str, Any]]:
    """Serialize command warnings."""
    return [
        {
            "kind": warning.kind,
            "message": warning.message,
        }
        for warning in warnings
    ]
