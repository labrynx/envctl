"""Command warning serializers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from envctl.domain.diagnostics import CommandWarning


def serialize_command_warnings(
    warnings: Sequence[CommandWarning],
) -> list[dict[str, Any]]:
    """Serialize command warnings."""
    return [
        {
            "kind": warning.kind,
            "message": warning.message,
        }
        for warning in warnings
    ]
