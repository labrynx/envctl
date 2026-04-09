"""Payload sanitization helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from envctl.observability.models import ObservationEvent, SanitizationPolicy
from envctl.utils.masking import mask_value

_SENSITIVE_KEY_TOKENS = (
    "secret",
    "token",
    "password",
    "passwd",
    "key",
    "private",
    "credential",
    "ciphertext",
    "plaintext",
    "rendered",
    "resolved",
    "payload",
)
_SEMANTIC_SENSITIVE_FIELDS = {"plaintext", "ciphertext", "master_key", "rendered"}
_FORBIDDEN_VAULT_FIELDS = {
    "master_key",
    "private_key",
    "raw_payload",
    "raw_vault_payload",
    "resolved_secret",
    "resolved_secrets",
    "plaintext",
    "ciphertext",
    "rendered",
}
_BLOCKED_VALUE = "[BLOCKED]"
_REDACTED_VALUE = "[REDACTED]"
_COUNT_ONLY_VALUE = "[COUNT_ONLY]"


def sanitize_event(
    event: ObservationEvent,
    *,
    policy: SanitizationPolicy = "masked",
) -> ObservationEvent:
    """Return an event copy sanitized according to one policy."""
    return ObservationEvent(
        event=sanitize_scalar(event.event, policy="full"),
        timestamp=event.timestamp,
        execution_id=sanitize_scalar(event.execution_id, policy="full"),
        status=sanitize_scalar(event.status, policy="full"),
        duration_ms=event.duration_ms,
        module=(sanitize_scalar(event.module, policy="full") if event.module is not None else None),
        operation=(
            sanitize_scalar(event.operation, policy="full") if event.operation is not None else None
        ),
        fields=sanitize_payload(event.fields or {}, policy=policy),
    )


def sanitize_payload(
    payload: Mapping[str, Any],
    *,
    policy: SanitizationPolicy = "masked",
) -> dict[str, Any]:
    """Redact sensitive key values in event payloads."""
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        sanitized[key] = sanitize_value(value, key=key, policy=policy)
    return sanitized


def sanitize_command(
    command: Sequence[str],
    *,
    policy: SanitizationPolicy = "masked",
) -> tuple[str, ...]:
    """Return one policy-aware sanitized command representation."""
    sanitized: list[str] = []
    for arg in command:
        if "=" in arg:
            key, value = arg.split("=", 1)
            safe_value = sanitize_value(value, key=key, policy=policy)
            sanitized.append(f"{key}={safe_value}")
            continue
        sanitized.append(sanitize_scalar(arg, policy=policy))
    return tuple(sanitized)


def sanitize_value(
    value: Any,
    *,
    key: str | None = None,
    policy: SanitizationPolicy = "masked",
) -> Any:
    """Sanitize one value optionally informed by a semantic key."""
    normalized_key = (key or "").strip().lower()
    if _is_forbidden_vault_field(normalized_key):
        return _BLOCKED_VALUE
    if _is_sensitive_key(normalized_key):
        return _sanitize_sensitive_value(value, policy=policy)

    if isinstance(value, Mapping):
        return {
            item_key: sanitize_value(item_value, key=item_key, policy=policy)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [sanitize_value(item, policy=policy) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_value(item, policy=policy) for item in value)
    if isinstance(value, set):
        return sorted(sanitize_value(item, policy=policy) for item in value)
    return sanitize_scalar(value, policy=policy)


def sanitize_scalar(value: Any, *, policy: SanitizationPolicy = "masked") -> Any:
    """Return one observability-safe scalar or summary value."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        if policy == "count_only" and isinstance(value, str):
            return _COUNT_ONLY_VALUE
        return value
    if isinstance(value, (list, tuple, set)):
        return f"<{type(value).__name__}:len={len(value)}>"
    if isinstance(value, Mapping):
        return f"<dict:len={len(value)}>"
    return f"<{type(value).__name__}>"


def _is_sensitive_key(normalized_key: str) -> bool:
    if normalized_key in _SEMANTIC_SENSITIVE_FIELDS:
        return True
    return any(token in normalized_key for token in _SENSITIVE_KEY_TOKENS)


def _is_forbidden_vault_field(normalized_key: str) -> bool:
    if not normalized_key:
        return False
    return normalized_key in _FORBIDDEN_VAULT_FIELDS


def _sanitize_sensitive_value(value: Any, *, policy: SanitizationPolicy) -> Any:
    if policy == "full":
        return sanitize_scalar(value, policy=policy)
    if policy == "count_only":
        if isinstance(value, Mapping):
            return f"{_COUNT_ONLY_VALUE}:dict:{len(value)}"
        if isinstance(value, (list, tuple, set)):
            return f"{_COUNT_ONLY_VALUE}:{len(value)}"
        if value is None:
            return _COUNT_ONLY_VALUE
        if isinstance(value, str):
            return _COUNT_ONLY_VALUE
        return _COUNT_ONLY_VALUE
    if isinstance(value, str):
        return mask_value(value)
    return _REDACTED_VALUE
