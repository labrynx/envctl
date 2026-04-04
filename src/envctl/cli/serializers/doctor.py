"""Doctor serializers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from envctl.domain.doctor import DoctorCheck


def serialize_doctor_checks(checks: Iterable[DoctorCheck]) -> dict[str, Any]:
    """Serialize doctor checks and aggregate their summary."""
    items = list(checks)
    has_failures = any(check.status == "fail" for check in items)

    return {
        "has_failures": has_failures,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "detail": check.detail,
            }
            for check in items
        ],
    }
