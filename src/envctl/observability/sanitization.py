"""Payload sanitization helpers."""

from typing import Any

SENSITIVE_KEYS = {"password", "secret", "token", "key"}


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive key values in event payloads."""

    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "[REDACTED]"
            continue
        sanitized[key] = sanitize_scalar(value)
    return sanitized


def sanitize_scalar(value: Any) -> Any:
    """Return one observability-safe scalar or summary value."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return f"<{type(value).__name__}:len={len(value)}>"
    if isinstance(value, dict):
        return f"<dict:len={len(value)}>"
    return f"<{type(value).__name__}>"
