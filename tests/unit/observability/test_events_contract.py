from __future__ import annotations

import pytest

from envctl.observability import clear_observability_context, initialize_observability_context
from envctl.observability.events import ALLOWED_EVENT_PREFIXES, event_prefix
from envctl.observability.recorder import record_event


def test_event_prefix_is_allowed_for_known_events() -> None:
    assert event_prefix("config.load.start") in ALLOWED_EVENT_PREFIXES
    assert event_prefix("vault.finish") in ALLOWED_EVENT_PREFIXES
    assert event_prefix("error.handled") in ALLOWED_EVENT_PREFIXES
    assert event_prefix("error.validation") in ALLOWED_EVENT_PREFIXES


def test_record_event_rejects_unknown_event_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    context = initialize_observability_context(command_name="check")

    assert context is not None
    with pytest.raises(ValueError, match="Unsupported observability event prefix"):
        record_event(
            context,
            event="demo.phase.finish",
            status="finish",
            module="tests",
            operation="demo",
            fields={},
        )
