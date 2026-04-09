"""Error taxonomy helpers for observability events."""

from __future__ import annotations

from dataclasses import dataclass

from envctl.errors import ConfigError, EnvctlError, ExecutionError, ValidationError
from envctl.observability.events import (
    ERROR_CONFIGURATION,
    ERROR_EXECUTION,
    ERROR_SECURITY,
    ERROR_UNEXPECTED,
    ERROR_VALIDATION,
)


@dataclass(frozen=True)
class ErrorEventMapping:
    """Mapped observability metadata for one exception."""

    event: str
    recoverable: bool
    message_safe: str


def map_exception_to_error_event(exc: Exception) -> ErrorEventMapping:
    """Map one exception to the canonical minimal error catalog."""
    if isinstance(exc, ConfigError):
        return ErrorEventMapping(
            event=ERROR_CONFIGURATION,
            recoverable=False,
            message_safe=str(exc),
        )
    if isinstance(exc, ValidationError | ValueError):
        return ErrorEventMapping(
            event=ERROR_VALIDATION,
            recoverable=True,
            message_safe=str(exc),
        )
    if isinstance(exc, PermissionError):
        return ErrorEventMapping(
            event=ERROR_SECURITY,
            recoverable=False,
            message_safe="Permission denied.",
        )
    if isinstance(exc, ExecutionError | OSError):
        return ErrorEventMapping(
            event=ERROR_EXECUTION,
            recoverable=False,
            message_safe=str(exc),
        )
    if isinstance(exc, EnvctlError):
        return ErrorEventMapping(
            event=ERROR_EXECUTION,
            recoverable=False,
            message_safe=str(exc),
        )
    return ErrorEventMapping(
        event=ERROR_UNEXPECTED,
        recoverable=False,
        message_safe="Unexpected internal error.",
    )
