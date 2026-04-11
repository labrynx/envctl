"""Event recording helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from envctl.observability.events import validate_event_name
from envctl.observability.models import ExecutionObservabilityContext, ObservationEvent
from envctl.observability.sanitization import sanitize_event
from envctl.observability.timing import utcnow


def record_event(
    context: ExecutionObservabilityContext,
    *,
    event: str,
    status: str,
    duration_ms: int | None = None,
    module: str | None = None,
    operation: str | None = None,
    fields: dict[str, Any] | None = None,
) -> ObservationEvent:
    """Create and dispatch one event for a context."""
    validate_event_name(event)

    observation = ObservationEvent(
        event=event,
        timestamp=utcnow(),
        execution_id=context.execution_id,
        status=status,
        duration_ms=duration_ms,
        module=module,
        operation=operation,
        fields=fields or {},
    )
    sanitized_observation = sanitize_event(observation, policy=context.sanitization_policy)

    if context.events is not None:
        context.events.append(sanitized_observation)

    for emitter in context.emitters:
        emitter.emit(sanitized_observation)

    return sanitized_observation


def duration_ms(started_at: datetime, ended_at: datetime) -> int:
    """Return elapsed milliseconds between two UTC timestamps."""
    delta = ended_at - started_at
    return int(delta.total_seconds() * 1000)
