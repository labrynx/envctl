"""Settings loading for observability features."""

from __future__ import annotations

import os
from dataclasses import dataclass

from envctl.observability.models import TraceFormat


@dataclass(frozen=True)
class ObservabilitySettings:
    """Runtime flags controlling observability behavior."""

    trace_enabled: bool
    trace_format: TraceFormat


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _parse_trace_format(value: str | None) -> TraceFormat:
    if value is None:
        return "json"
    normalized = value.strip().lower()
    if normalized in {"json", "text"}:
        return normalized
    return "json"


def load_observability_settings() -> ObservabilitySettings:
    """Read observability flags from environment variables."""

    return ObservabilitySettings(
        trace_enabled=_parse_bool(os.getenv("ENVCTL_OBSERVABILITY_TRACE")),
        trace_format=_parse_trace_format(os.getenv("ENVCTL_OBSERVABILITY_TRACE_FORMAT")),
    )
