"""Timing helpers for observability."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any


def utcnow() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(UTC)


@contextmanager
def observe_span(
    event_prefix: str,
    *,
    module: str | None = None,
    operation: str | None = None,
    fields: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Emit start/finish/error events around one operation span."""

    from envctl.observability import get_active_observability_context
    from envctl.observability.recorder import duration_ms, record_event

    started_at = utcnow()
    span_fields = dict(fields or {})
    context = get_active_observability_context()
    if context is not None:
        record_event(
            context,
            event=f"{event_prefix}.start",
            status="start",
            module=module,
            operation=operation,
            fields=span_fields,
        )
    try:
        yield span_fields
    except Exception:
        if context is not None:
            record_event(
                context,
                event=f"{event_prefix}.error",
                status="error",
                duration_ms=duration_ms(started_at),
                module=module,
                operation=operation,
                fields=span_fields,
            )
        raise
    if context is not None:
        record_event(
            context,
            event=f"{event_prefix}.finish",
            status="finish",
            duration_ms=duration_ms(started_at),
            module=module,
            operation=operation,
            fields=span_fields,
        )
