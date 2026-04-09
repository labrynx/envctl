"""Rendering helpers for observability events."""

from __future__ import annotations

import json

from envctl.observability.models import ObservabilityEvent, TraceFormat


def render_event(event: ObservabilityEvent, trace_format: TraceFormat) -> str:
    """Render one event in the selected output format."""

    if trace_format == "text":
        return f"{event.timestamp.isoformat()} {event.name} {event.payload}"
    return json.dumps(
        {
            "timestamp": event.timestamp.isoformat(),
            "name": event.name,
            "payload": event.payload,
        },
        sort_keys=True,
    )
