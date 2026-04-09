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


def test_sanitize_event_blocks_vault_material_to_prevent_secret_leakage() -> None:
    event = sanitize_event(
        _event(
            {
                "raw_vault_payload": "ENC[AES256_GCM,data:super-secret]",
                "resolved_secrets": {"DATABASE_URL": "postgres://user:pass@db/app"},
                "private_key": "-----BEGIN PRIVATE KEY-----...",
                "profile": "local",
            }
        )
    )

    assert event.fields == {
        "raw_vault_payload": "[BLOCKED]",
        "resolved_secrets": "[BLOCKED]",
        "private_key": "[BLOCKED]",
        "profile": "local",
    }


def test_sanitize_command_masks_sensitive_flag_assignments() -> None:
    sanitized = sanitize_command(
        [
            "run",
            "--api-token=ghp_very_secret_token",
            "--db-password=hunter2",
            "--profile=local",
        ]
    )

    assert sanitized[0] == "run"
    assert sanitized[1].startswith("--api-token=gh")
    assert sanitized[1] != "--api-token=ghp_very_secret_token"
    assert sanitized[2] == "--db-password=hu*****"
    assert sanitized[3] == "--profile=local"
