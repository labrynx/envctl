from __future__ import annotations

import pytest

from envctl.observability import clear_observability_context, initialize_observability_context
from envctl.observability.timing import observe_span


def test_observe_span_emits_start_and_finish_events(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    context = initialize_observability_context(command_name="check")

    assert context is not None
    with observe_span("demo.phase", module="tests", operation="test") as fields:
        fields["items"] = 2

    assert context.events is not None
    assert [event.event for event in context.events] == ["demo.phase.start", "demo.phase.finish"]
    assert context.events[-1].fields == {"items": 2}
    assert context.events[-1].duration_ms is not None


def test_observe_span_emits_error_event_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    context = initialize_observability_context(command_name="check")

    assert context is not None
    with pytest.raises(RuntimeError, match="boom"), observe_span(
        "demo.phase", module="tests", operation="test"
    ):
        raise RuntimeError("boom")

    assert context.events is not None
    assert [event.event for event in context.events] == ["demo.phase.start", "demo.phase.error"]
    assert context.events[-1].duration_ms is not None
