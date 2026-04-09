from __future__ import annotations

from envctl.observability.models import ObservationEvent
from envctl.observability.sanitization import sanitize_command, sanitize_event, sanitize_payload
from envctl.observability.timing import utcnow


def _event(fields: dict[str, object]) -> ObservationEvent:
    return ObservationEvent(
        event="vault.finish",
        timestamp=utcnow(),
        execution_id="exec-1",
        status="finish",
        duration_ms=11,
        module="tests",
        operation="run",
        fields=fields,
    )


def test_sanitize_event_masks_sensitive_fields_by_default() -> None:
    event = sanitize_event(
        _event({"plaintext": "supersecret", "profile": "local", "token": "abcd"})
    )

    assert event.fields == {
        "plaintext": "[BLOCKED]",
        "profile": "local",
        "token": "****",
    }


def test_sanitize_event_count_only_policy_reduces_sensitive_material() -> None:
    event = sanitize_event(
        _event({"master_key": "abc123", "resolved_secret": "xyz", "key_count": 2}),
        policy="count_only",
    )

    assert event.fields == {
        "master_key": "[BLOCKED]",
        "resolved_secret": "[BLOCKED]",
        "key_count": "[COUNT_ONLY]",
    }


def test_sanitize_payload_recurses_for_nested_values() -> None:
    payload = sanitize_payload({"meta": {"token": "abcdef", "ok": True}})
    assert payload == {"meta": {"token": "ab****", "ok": True}}


def test_sanitize_command_masks_assignment_values() -> None:
    assert sanitize_command(["run", "PASSWORD=hunter2", "PLAIN=ok"]) == (
        "run",
        "PASSWORD=hu*****",
        "PLAIN=ok",
    )
