from __future__ import annotations

from collections.abc import Mapping, Sequence

from envctl.domain.resolution import ResolutionReport, ResolvedValue


def make_resolved_value(
    *,
    key: str,
    value: str,
    source: str = "vault",
    masked: bool = False,
    valid: bool = True,
    detail: str | None = None,
) -> ResolvedValue:
    """Build one resolved value."""
    return ResolvedValue(
        key=key,
        value=value,
        source=source,
        masked=masked,
        valid=valid,
        detail=detail,
    )


def make_resolution_report(
    *,
    values: Mapping[str, ResolvedValue] | None = None,
    missing_required: Sequence[str] | None = None,
    unknown_keys: Sequence[str] | None = None,
    invalid_keys: Sequence[str] | None = None,
) -> ResolutionReport:
    """Build a resolution report with sensible defaults."""
    return ResolutionReport.from_parts(
        values=dict(values or {}),
        missing_required=tuple(missing_required or ()),
        unknown_keys=tuple(unknown_keys or ()),
        invalid_keys=tuple(invalid_keys or ()),
    )