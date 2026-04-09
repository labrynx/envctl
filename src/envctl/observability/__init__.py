"""Public observability API."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from envctl.observability.context import (
    clear_active_context,
    get_active_context,
    set_active_context,
)
from envctl.observability.emitters import (
    FileEmitter,
    NullEmitter,
    ObservabilityEmitter,
    StreamEmitter,
)
from envctl.observability.models import (
    ExecutionObservabilityContext,
    SanitizationPolicy,
    TraceFormat,
    TraceOutput,
)
from envctl.observability.settings import load_observability_settings
from envctl.observability.timing import utcnow

__all__ = [
    "ExecutionObservabilityContext",
    "clear_observability_context",
    "get_active_observability_context",
    "initialize_observability_context",
]


def _default_trace_file(*, trace_format: TraceFormat) -> Path:
    extension = "jsonl" if trace_format == "jsonl" else "txt"
    return Path.cwd() / ".envctl" / "observability" / f"latest.{extension}"


def initialize_observability_context(
    command_name: str,
    *,
    trace_enabled: bool | None = None,
    trace_format: TraceFormat | None = None,
    trace_output: TraceOutput | None = None,
    trace_file: Path | None = None,
    profile_observability: bool | None = None,
    sanitization_policy: SanitizationPolicy | None = None,
) -> ExecutionObservabilityContext | None:
    """Initialize active observability context for one CLI invocation."""

    settings = load_observability_settings()
    resolved_trace_enabled = settings.trace_enabled if trace_enabled is None else trace_enabled
    if not resolved_trace_enabled:
        clear_active_context()
        return None

    resolved_trace_format = settings.trace_format if trace_format is None else trace_format
    resolved_trace_output = settings.trace_output if trace_output is None else trace_output
    resolved_trace_file = settings.trace_file if trace_file is None else trace_file
    resolved_profile = (
        settings.profile_observability if profile_observability is None else profile_observability
    )
    resolved_sanitization_policy = (
        settings.sanitization_policy if sanitization_policy is None else sanitization_policy
    )

    emitters: list[ObservabilityEmitter] = []
    effective_trace_file: Path | None = resolved_trace_file

    if resolved_trace_output in {"stderr", "both"}:
        emitters.append(
            StreamEmitter(
                trace_format=resolved_trace_format,
                sanitization_policy=resolved_sanitization_policy,
            )
        )
    if resolved_trace_output in {"file", "both"}:
        target_file = resolved_trace_file or _default_trace_file(trace_format=resolved_trace_format)
        effective_trace_file = target_file
        emitters.append(
            FileEmitter(
                path=target_file,
                trace_format=resolved_trace_format,
                sanitization_policy=resolved_sanitization_policy,
            )
        )

    if not emitters:
        emitters.append(NullEmitter())

    context = ExecutionObservabilityContext(
        execution_id=str(uuid4()),
        command_name=command_name,
        trace_enabled=resolved_trace_enabled,
        profile_observability=resolved_profile,
        trace_format=resolved_trace_format,
        trace_output=resolved_trace_output,
        trace_file=effective_trace_file,
        sanitization_policy=resolved_sanitization_policy,
        start_time=utcnow(),
        emitters=tuple(emitters),
        events=[],
    )
    set_active_context(context)
    return context


def get_active_observability_context() -> ExecutionObservabilityContext | None:
    """Return currently active observability context, if any."""

    return get_active_context()


def clear_observability_context() -> None:
    """Clear currently active observability context."""

    clear_active_context()
