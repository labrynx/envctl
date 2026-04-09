from __future__ import annotations

import json
from pathlib import Path

from envctl.observability.emitters import FileEmitter
from envctl.observability.models import ObservationEvent
from envctl.observability.recorder import record_event
from envctl.observability.timing import utcnow


class MemoryEmitter:
    """Simple in-memory emitter used to validate emitter contracts."""

    def __init__(self) -> None:
        self.events: list[ObservationEvent] = []

    def emit(self, event: ObservationEvent) -> None:
        self.events.append(event)


def test_memory_emitter_collects_observation_events() -> None:
    event = ObservationEvent(
        event="resolution.finish",
        timestamp=utcnow(),
        execution_id="exec-1",
        status="finish",
        duration_ms=18,
        module="tests.observability",
        operation="resolve",
        fields={"profile": "local"},
    )

    emitter = MemoryEmitter()
    emitter.emit(event)

    assert emitter.events == [event]


def test_file_emitter_jsonl_renders_valid_event_payload(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    emitter = FileEmitter(path=path, trace_format="jsonl")
    emitter.emit(
        ObservationEvent(
            event="resolution.finish",
            timestamp=utcnow(),
            execution_id="exec-1",
            status="finish",
            duration_ms=25,
            module="tests.observability",
            operation="resolve",
            fields={"profile": "local", "token": "super-secret"},
        )
    )

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["event"] == "resolution.finish"
    assert payload["execution_id"] == "exec-1"
    assert payload["status"] == "finish"
    assert payload["duration_ms"] == 25
    assert payload["fields"] == {"profile": "local", "token": "su**********"}


def test_observation_event_shape_has_backwards_compatible_aliases() -> None:
    event = ObservationEvent(
        event="run.exec.finish",
        timestamp=utcnow(),
        execution_id="exec-1",
        status="finish",
        duration_ms=41,
        module="envctl.services.run_service",
        operation="run_command",
        fields={"arg_count": 3, "command_head": "python"},
    )

    assert event.name == "run.exec.finish"
    assert event.payload == {
        "execution_id": "exec-1",
        "status": "finish",
        "duration_ms": 41,
        "module": "envctl.services.run_service",
        "operation": "run_command",
        "fields": {"arg_count": 3, "command_head": "python"},
    }


def test_record_event_appends_into_custom_memory_emitter() -> None:
    from envctl.observability.models import ExecutionObservabilityContext

    memory = MemoryEmitter()
    context = ExecutionObservabilityContext(
        execution_id="exec-1",
        command_name="check",
        trace_enabled=True,
        profile_observability=False,
        trace_format="human",
        trace_output="stderr",
        trace_file=None,
        sanitization_policy="masked",
        start_time=utcnow(),
        emitters=(memory,),
        events=[],
    )

    event = record_event(
        context,
        event="context.resolve.finish",
        status="finish",
        duration_ms=12,
        fields={"profile": "local", "token": "abcdef"},
    )

    assert memory.events == [event]
    assert memory.events[0].fields == {"profile": "local", "token": "ab****"}
