"""Timing helpers for observability."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from time import perf_counter_ns
from typing import Any


def utcnow() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def monotonic_now_ns() -> int:
    """Return monotonic time in nanoseconds for elapsed-time measurements."""

    return perf_counter_ns()


def elapsed_ms(started_ns: int, ended_ns: int) -> int:
    """Return elapsed milliseconds between two monotonic timestamps."""

    if ended_ns < started_ns:
        raise ValueError("ended_ns must be greater than or equal to started_ns")
    return (ended_ns - started_ns) // 1_000_000


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
    from envctl.observability.error_mapping import map_exception_to_error_event
    from envctl.observability.recorder import record_event

    started_ns = monotonic_now_ns()
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
    except Exception as exc:
        if context is not None:
            mapping = map_exception_to_error_event(exc)
            span_fields.setdefault("error_type", exc.__class__.__name__)
            span_fields.setdefault("error_kind", mapping.event)
            span_fields.setdefault("handled", False)
            span_fields.setdefault("recoverable", mapping.recoverable)
            span_fields.setdefault("message_safe", mapping.message_safe)
            record_event(
                context,
                event=f"{event_prefix}.error",
                status="error",
                duration_ms=elapsed_ms(started_ns, monotonic_now_ns()),
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
            duration_ms=elapsed_ms(started_ns, monotonic_now_ns()),
            module=module,
            operation=operation,
            fields=span_fields,
        )
