"""Export command JSON serializers."""

from __future__ import annotations

from typing import Literal


def serialize_export_result(
    *,
    active_profile: str,
    format: Literal["shell", "dotenv"],
    values: dict[str, str],
    rendered: str,
) -> dict[str, object]:
    """Serialize one export result for automation-friendly CLI JSON output."""
    return {
        "active_profile": active_profile,
        "format": format,
        "values": dict(values),
        "rendered": rendered,
    }
