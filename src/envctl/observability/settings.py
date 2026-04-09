"""Settings loading for observability features."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from envctl.observability.models import SanitizationPolicy, TraceFormat, TraceOutput


@dataclass(frozen=True)
class ObservabilitySettings:
    """Runtime flags controlling observability behavior."""

    trace_enabled: bool
    profile_observability: bool
    trace_format: TraceFormat
    trace_output: TraceOutput
    trace_file: Path | None
    sanitization_policy: SanitizationPolicy


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _parse_trace_format(value: str | None) -> TraceFormat:
    if value is None:
        return "jsonl"
    normalized = value.strip().lower()
    if normalized in {"jsonl", "json"}:
        return "jsonl"
    if normalized in {"human", "text"}:
        return "human"
    return "jsonl"


def _parse_trace_output(value: str | None) -> TraceOutput:
    if value is None:
        return "stderr"
    normalized = value.strip().lower()
    if normalized == "stderr":
        return "stderr"
    if normalized == "file":
        return "file"
    if normalized == "both":
        return "both"
    return "stderr"


def _parse_sanitization_policy(value: str | None) -> SanitizationPolicy:
    if value is None:
        return "masked"
    normalized = value.strip().lower()
    if normalized == "full":
        return "full"
    if normalized == "masked":
        return "masked"
    if normalized == "count_only":
        return "count_only"
    return "masked"


def load_observability_settings() -> ObservabilitySettings:
    """Read observability flags from environment variables."""

    return ObservabilitySettings(
        trace_enabled=_parse_bool(os.getenv("ENVCTL_OBSERVABILITY_TRACE")),
        profile_observability=_parse_bool(os.getenv("ENVCTL_OBSERVABILITY_PROFILE")),
        trace_format=_parse_trace_format(os.getenv("ENVCTL_OBSERVABILITY_TRACE_FORMAT")),
        trace_output=_parse_trace_output(os.getenv("ENVCTL_OBSERVABILITY_TRACE_OUTPUT")),
        trace_file=(
            Path(raw_trace_file).expanduser()
            if (raw_trace_file := os.getenv("ENVCTL_OBSERVABILITY_TRACE_FILE"))
            else None
        ),
        sanitization_policy=_parse_sanitization_policy(
            os.getenv("ENVCTL_OBSERVABILITY_SANITIZATION")
        ),
    )
