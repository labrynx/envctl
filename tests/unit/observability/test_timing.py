from __future__ import annotations

import pytest

from envctl.observability import clear_observability_context, initialize_observability_context
from envctl.observability.timing import observe_span


def test_observe_span_emits_start_and_finish_events(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    context = initialize_observability_context(command_name="check")

    assert context is not None
    with observe_span("resolution", module="tests", operation="test") as fields:
        fields["items"] = 2

    assert context.events is not None
    assert [event.event for event in context.events] == ["resolution.start", "resolution.finish"]
    event = context.events[-1]
    assert event.fields == {"items": 2}
    assert event.duration_ms is not None


def test_observe_span_emits_error_event_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    context = initialize_observability_context(command_name="check")

    assert context is not None
    with pytest.raises(RuntimeError, match="boom"):
        with observe_span("resolution", module="tests", operation="test"):
            raise RuntimeError("boom")

    assert context.events is not None
    assert [event.event for event in context.events] == ["resolution.start", "resolution.error"]
    event = context.events[-1]
    assert event.duration_ms is not None

    fields = event.fields
    assert fields is not None
    assert fields["error_type"] == "RuntimeError"
    assert fields["handled"] is False
    assert fields["recoverable"] is False
    assert fields["message_safe"] == "Unexpected internal error."
