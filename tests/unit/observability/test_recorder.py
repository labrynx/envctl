from __future__ import annotations

from datetime import timedelta

from envctl.observability.models import ExecutionObservabilityContext
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow


class _Emitter:
    def __init__(self) -> None:
        self.events = []

    def emit(self, event) -> None:
        self.events.append(event)


def test_record_event_builds_stable_observation_event() -> None:
    emitter = _Emitter()
    context = ExecutionObservabilityContext(
        execution_id="exec-1",
        command_name="check",
        trace_enabled=True,
        trace_format="json",
        start_time=utcnow(),
        emitters=(emitter,),
        events=[],
    )

    event = record_event(
        context,
        event="resolution.start",
        status="start",
        module="envctl.services.resolution_service.resolution",
        operation="resolve_environment",
        fields={"profile": "local", "token": "secret-value"},
    )

    assert event.event == "resolution.start"
    assert event.execution_id == "exec-1"
    assert event.status == "start"
    assert event.module == "envctl.services.resolution_service.resolution"
    assert event.operation == "resolve_environment"
    assert event.fields == {"profile": "local", "token": "[REDACTED]"}
    assert context.events == [event]
    assert emitter.events == [event]


def test_duration_ms_returns_positive_elapsed_time() -> None:
    started_at = utcnow()
    ended_at = started_at + timedelta(milliseconds=123)

    assert duration_ms(started_at, ended_at) == 123
