"""Deprecation warning serializers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from envctl.domain.deprecations import ContractDeprecationWarning


def serialize_contract_deprecation_warnings(
    warnings: Sequence[ContractDeprecationWarning],
) -> list[dict[str, Any]]:
    """Serialize normalized contract deprecation warnings."""
    return [
        {
            "key": warning.key,
            "deprecated_field": warning.deprecated_field,
            "message": warning.message,
        }
        for warning in warnings
    ]
