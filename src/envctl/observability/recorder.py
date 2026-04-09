"""Event recording helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from envctl.observability.models import ExecutionObservabilityContext, ObservationEvent
from envctl.observability.sanitization import sanitize_payload, sanitize_scalar
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

    observation = ObservationEvent(
        event=event,
        timestamp=utcnow(),
        execution_id=context.execution_id,
        status=sanitize_scalar(status),
        duration_ms=duration_ms,
        module=sanitize_scalar(module) if module is not None else None,
        operation=sanitize_scalar(operation) if operation is not None else None,
        fields=sanitize_payload(fields or {}),
    )

    if context.events is not None:
        context.events.append(observation)

    for emitter in context.emitters:
        emitter.emit(observation)

    return observation


def duration_ms(started_at: datetime, ended_at: datetime | None = None) -> int:
    """Return elapsed milliseconds between two UTC timestamps."""
    end = ended_at or utcnow()
    elapsed = end - started_at
    return max(0, int(elapsed.total_seconds() * 1000))
