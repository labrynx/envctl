"""Payload sanitization helpers."""

from __future__ import annotations

from typing import Any


SENSITIVE_KEYS = {"password", "secret", "token", "key"}


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive key values in event payloads."""

    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "[REDACTED]"
            continue
        sanitized[key] = value
    return sanitized
