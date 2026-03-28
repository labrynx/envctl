"""Resolution domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResolvedValue:
    """Single resolved environment value."""

    key: str
    value: str
    source: str
    masked: bool
    valid: bool = True
    detail: str | None = None


@dataclass(frozen=True)
class ResolutionReport:
    """Resolved environment state."""

    values: dict[str, ResolvedValue]
    missing_required: list[str]
    unknown_keys: list[str]
    invalid_keys: list[str]

    @property
    def is_valid(self) -> bool:
        """Return whether the full resolved state is valid."""
        return not self.missing_required and not self.invalid_keys
