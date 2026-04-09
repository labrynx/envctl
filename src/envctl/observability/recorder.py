"""Event recording helpers."""

from __future__ import annotations

from typing import Any

from envctl.observability.models import ExecutionObservabilityContext, ObservabilityEvent
from envctl.observability.sanitization import sanitize_payload
from envctl.observability.timing import utcnow


def record_event(
    context: ExecutionObservabilityContext,
    *,
    name: str,
    payload: dict[str, Any] | None = None,
) -> ObservabilityEvent:
    """Create and dispatch one event for a context."""

    event = ObservabilityEvent(
        name=name,
        payload=sanitize_payload(payload or {}),
        timestamp=utcnow(),
    )

    if context.events is not None:
        context.events.append(event)

    for emitter in context.emitters:
        emitter.emit(event)

    return event
