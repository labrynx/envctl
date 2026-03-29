"""Contract inference helpers."""

from __future__ import annotations

import re

from envctl.domain.contract import VariableSpec, VariableType

_SECRET_KEY_PARTS = {
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PASS",
    "API_KEY",
    "PRIVATE_KEY",
    "ACCESS_KEY",
    "CLIENT_SECRET",
    "JWT",
}

_PUBLIC_URL_HINTS = {
    "PUBLIC_URL",
    "BASE_URL",
    "APP_URL",
    "SITE_URL",
}

_DESCRIPTION_MAP = {
    "APP_NAME": "Application name",
    "PORT": "Application port",
    "DEBUG": "Debug mode",
    "DATABASE_URL": "Primary database connection URL",
    "REDIS_URL": "Redis connection URL",
    "NODE_ENV": "Runtime environment",
    "ENVIRONMENT": "Runtime environment",
    "LOG_LEVEL": "Application log level",
    "HOST": "Application host",
    "SERVICE_NAME": "Service name",
    "SLUG": "Application slug",
}

_ENVIRONMENT_CHOICES = ("development", "test", "staging", "production")
_SHORT_ENVIRONMENT_CHOICES = ("dev", "staging", "prod")
_LOG_LEVEL_CHOICES = ("debug", "info", "warning", "error", "critical")

_PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "change-me",
    "replace-me",
    "example",
    "todo",
    "tbd",
    "your-api-key-here",
    "your_api_key_here",
    "your-token-here",
    "your_token_here",
}


def infer_type(key: str, value: str) -> VariableType:
    """Infer the variable type from key and value."""
    upper = key.upper()
    stripped = value.strip()

    if upper == "PORT" or upper.endswith("_PORT"):
        return "int"

    if upper == "DEBUG" or upper.startswith("ENABLE_") or upper.startswith("USE_"):
        return "bool"

    if stripped.lower() in {"true", "false", "1", "0", "yes", "no"}:
        return "bool"

    if re.fullmatch(r"-?\d+", stripped):
        return "int"

    if upper.endswith("_URL"):
        return "url"

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", stripped):
        return "url"

    return "string"


def infer_sensitive(key: str) -> bool:
    """Infer whether the variable should be treated as sensitive."""
    upper = key.upper()

    if upper in _PUBLIC_URL_HINTS:
        return False

    if upper.endswith("_URL"):
        return upper not in _PUBLIC_URL_HINTS

    return any(part in upper for part in _SECRET_KEY_PARTS)


def infer_description(key: str) -> str:
    """Infer a human-readable description."""
    upper = key.upper()

    if upper in _DESCRIPTION_MAP:
        return _DESCRIPTION_MAP[upper]

    words = upper.split("_")
    human = " ".join(word.lower() for word in words)
    return human[:1].upper() + human[1:]


def infer_choices(key: str, value: str) -> tuple[str, ...]:
    """Infer choices for well-known variables."""
    upper = key.upper()
    lowered = value.strip().lower()

    if upper == "NODE_ENV":
        return _ENVIRONMENT_CHOICES

    if upper == "ENVIRONMENT":
        if lowered in _SHORT_ENVIRONMENT_CHOICES:
            return _SHORT_ENVIRONMENT_CHOICES
        if lowered in _ENVIRONMENT_CHOICES:
            return _ENVIRONMENT_CHOICES

    if upper == "LOG_LEVEL":
        return _LOG_LEVEL_CHOICES

    return ()


def infer_pattern(key: str, value: str) -> str | None:
    """Infer a validation pattern when obvious and safe."""
    upper = key.upper()
    stripped = value.strip()

    if upper in {"APP_NAME", "SERVICE_NAME", "SLUG"} and re.fullmatch(r"[a-z0-9-]+", stripped):
        return r"^[a-z0-9-]+$"

    return None


def looks_like_placeholder(value: str) -> bool:
    """Return whether a value looks like a placeholder."""
    normalized = value.strip().lower()

    if normalized in _PLACEHOLDER_VALUES:
        return True

    if normalized.startswith("<") and normalized.endswith(">"):
        return True

    if normalized.startswith("your_") or normalized.startswith("your-"):
        return True

    return "changeme" in normalized or "replace" in normalized


def infer_default(key: str, value: str, inferred_type: VariableType) -> str | int | bool | None:
    """Infer a conservative default value when appropriate."""
    if looks_like_placeholder(value):
        return None

    stripped = value.strip()

    if inferred_type == "int":
        try:
            return int(stripped)
        except ValueError:
            return None

    if inferred_type == "bool":
        lowered = stripped.lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False

    return None


def infer_example(
    key: str,
    value: str,
    *,
    inferred_type: VariableType,
    sensitive: bool,
) -> str | None:
    """Infer an example value when it is safe and useful."""
    if looks_like_placeholder(value):
        return None

    stripped = value.strip()
    upper = key.upper()

    if inferred_type == "url":
        return stripped

    if not sensitive and upper in {
        "APP_NAME",
        "SERVICE_NAME",
        "HOST",
        "NODE_ENV",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "SLUG",
    }:
        return stripped

    if not sensitive and stripped:
        return stripped

    return None


def infer_spec(key: str, value: str) -> VariableSpec:
    """Build an inferred VariableSpec from key and value."""
    inferred_type = infer_type(key, value)
    sensitive = infer_sensitive(key)

    return VariableSpec(
        name=key,
        type=inferred_type,
        required=True,
        sensitive=sensitive,
        description=infer_description(key),
        default=infer_default(key, value, inferred_type),
        example=infer_example(
            key,
            value,
            inferred_type=inferred_type,
            sensitive=sensitive,
        ),
        pattern=infer_pattern(key, value),
        choices=infer_choices(key, value),
    )
