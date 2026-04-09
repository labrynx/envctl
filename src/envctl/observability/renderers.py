"""Rendering helpers for observability events."""

from __future__ import annotations

import json

from envctl.observability.models import ObservationEvent, TraceFormat


def render_event(event: ObservationEvent, trace_format: TraceFormat) -> str:
    """Render one event in the selected output format."""

    if trace_format == "text":
        return f"{event.timestamp.isoformat()} {event.event} {event.payload}"
    return json.dumps(
        {
            "timestamp": event.timestamp.isoformat(),
            "event": event.event,
            "execution_id": event.execution_id,
            "status": event.status,
            "duration_ms": event.duration_ms,
            "module": event.module,
            "operation": event.operation,
            "fields": event.fields or {},
        },
        sort_keys=True,
    )
