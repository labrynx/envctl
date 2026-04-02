"""Resolution domain models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from envctl.domain.expansion import ExpansionErrorInfo, ExpansionStatus


@dataclass(frozen=True)
class ResolvedValue:
    """Single resolved environment value."""

    key: str
    value: str
    source: str
    masked: bool
    raw_value: str | None = None
    expansion_status: ExpansionStatus = "none"
    expansion_refs: tuple[str, ...] = ()
    expansion_error: ExpansionErrorInfo | None = None
    valid: bool = True
    detail: str | None = None


@dataclass(frozen=True)
class ResolutionReport:
    """Resolved environment state."""

    values: Mapping[str, ResolvedValue]
    missing_required: tuple[str, ...]
    unknown_keys: tuple[str, ...]
    invalid_keys: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether the full resolved state is valid."""
        return not self.missing_required and not self.invalid_keys

    @classmethod
    def from_parts(
        cls,
        *,
        values: Mapping[str, ResolvedValue],
        missing_required: Sequence[str],
        unknown_keys: Sequence[str],
        invalid_keys: Sequence[str],
    ) -> ResolutionReport:
        """Build an immutable resolution report from input collections."""
        return cls(
            values=MappingProxyType(dict(values)),
            missing_required=tuple(missing_required),
            unknown_keys=tuple(unknown_keys),
            invalid_keys=tuple(invalid_keys),
        )
