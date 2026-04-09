"""Public observability API."""

from __future__ import annotations

from uuid import uuid4

from envctl.observability.context import clear_active_context, get_active_context, set_active_context
from envctl.observability.emitters import NullEmitter
from envctl.observability.models import ExecutionObservabilityContext
from envctl.observability.settings import load_observability_settings
from envctl.observability.timing import utcnow

__all__ = [
    "ExecutionObservabilityContext",
    "clear_observability_context",
    "get_active_observability_context",
    "initialize_observability_context",
]


def initialize_observability_context(command_name: str) -> ExecutionObservabilityContext | None:
    """Initialize active observability context for one CLI invocation."""

    settings = load_observability_settings()
    if not settings.trace_enabled:
        clear_active_context()
        return None

    context = ExecutionObservabilityContext(
        execution_id=str(uuid4()),
        command_name=command_name,
        trace_enabled=settings.trace_enabled,
        trace_format=settings.trace_format,
        start_time=utcnow(),
        emitters=(NullEmitter(),),
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
