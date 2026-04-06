"""Contract deprecation warning models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DeprecatedField = Literal["group", "required"]


@dataclass(frozen=True)
class ContractDeprecationWarning:
    """One normalized contract deprecation warning."""

    key: str
    deprecated_field: DeprecatedField
    message: str


def make_group_deprecation_warning(key: str, value: str) -> ContractDeprecationWarning:
    """Build the preferred deprecation warning for legacy `group`."""
    return ContractDeprecationWarning(
        key=key,
        deprecated_field="group",
        message=(
            f"Warning: variable '{key}' uses deprecated key 'group'.\n"
            f"It is still supported and will be treated as 'groups: [{value}]', "
            "but you should migrate to 'groups' with an array of values before v2.6.0."
        ),
    )


def make_required_deprecation_warning(key: str) -> ContractDeprecationWarning:
    """Build the preferred deprecation warning for legacy `required`."""
    return ContractDeprecationWarning(
        key=key,
        deprecated_field="required",
        message=(
            f"Warning: variable '{key}' uses deprecated key 'required'.\n"
            "This key no longer has meaning and will be ignored. "
            "Remove it before v2.6.0. Validation is now driven by the active "
            "contract scope (full contract, --set, --group, or --var)."
        ),
    )
