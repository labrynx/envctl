from __future__ import annotations

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
    values: dict[str, ResolvedValue] | None = None,
    missing_required: list[str] | None = None,
    unknown_keys: list[str] | None = None,
    invalid_keys: list[str] | None = None,
) -> ResolutionReport:
    """Build a resolution report with sensible defaults."""
    return ResolutionReport(
        values=values or {},
        missing_required=missing_required or [],
        unknown_keys=unknown_keys or [],
        invalid_keys=invalid_keys or [],
    )
