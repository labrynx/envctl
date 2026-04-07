"""Internal logging helpers for envctl."""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence, Sized

from envctl.utils.masking import mask_value

ENVCTL_LOG_LEVEL_ENVVAR = "ENVCTL_LOG_LEVEL"
_ALLOWED_LOG_LEVELS = {"DEBUG", "WARNING", "ERROR"}
_DEFAULT_LOG_LEVEL = "WARNING"
_ENVCTL_LOGGER_NAME = "envctl"
_RESERVED_LOG_RECORD_KEYS = set(logging.makeLogRecord({}).__dict__.keys()) | {
    "asctime",
    "message",
}


class _EnvctlDebugFormatter(logging.Formatter):
    """Stable formatter for internal debug output."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        context = _format_context(record)
        if context:
            return f"{message} | {context}"
        return message


def _format_context(record: logging.LogRecord) -> str:
    context: list[str] = []
    for key in sorted(record.__dict__):
        if key.startswith("_") or key in _RESERVED_LOG_RECORD_KEYS:
            continue
        value = record.__dict__[key]
        context.append(f"{key}={value}")
    return " ".join(context)


def _resolve_log_level_name() -> str:
    raw = os.environ.get(ENVCTL_LOG_LEVEL_ENVVAR, _DEFAULT_LOG_LEVEL)
    normalized = str(raw).strip().upper()
    if normalized in _ALLOWED_LOG_LEVELS:
        return normalized
    return _DEFAULT_LOG_LEVEL


def _resolve_log_level() -> int:
    return getattr(logging, _resolve_log_level_name(), logging.WARNING)


def _get_envctl_logger() -> logging.Logger:
    return logging.getLogger(_ENVCTL_LOGGER_NAME)


def ensure_logging_configured() -> None:
    """Ensure the envctl logger tree is configured once for internal tracing."""
    envctl_logger = _get_envctl_logger()
    target_level = _resolve_log_level()

    if not any(getattr(handler, "_envctl_handler", False) for handler in envctl_logger.handlers):
        handler = logging.StreamHandler()
        handler._envctl_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(
            _EnvctlDebugFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        envctl_logger.addHandler(handler)

    envctl_logger.setLevel(target_level)
    envctl_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return one configured logger for internal envctl tracing."""
    ensure_logging_configured()
    return logging.getLogger(name)


def mask_value_for_log(value: str, *, sensitive: bool = True) -> str:
    """Return a safe value representation for debug logging."""
    if sensitive:
        return mask_value(value)
    return value


def summarize_keys(keys: Sequence[str], *, limit: int = 8) -> str:
    """Build a compact comma-separated key summary for debug logging."""
    if not keys:
        return "-"

    ordered = list(keys)
    preview = ", ".join(ordered[:limit])
    if len(ordered) <= limit:
        return preview
    return f"{preview}, … (+{len(ordered) - limit} more)"


def summarize_key_count(keys: Sized) -> str:
    """Return a count-only summary for potentially sensitive key sets."""
    count = len(keys)
    if count == 0:
        return "0"
    if count == 1:
        return "1 key"
    return f"{count} keys"


def sanitize_command_for_log(command: Sequence[str]) -> tuple[str, ...]:
    """Return one best-effort sanitized command preview for debug logging."""
    return tuple(_sanitize_arg(arg) for arg in command)


def _sanitize_arg(arg: str) -> str:
    if "=" in arg:
        key, value = arg.split("=", 1)
        if _looks_sensitive_key(key):
            return f"{key}={mask_value(value)}"
    return arg


def _looks_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    return any(token in normalized for token in ("secret", "token", "password", "passwd", "key"))
