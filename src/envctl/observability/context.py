"""Context-local storage for observability state."""

from __future__ import annotations

from contextvars import ContextVar

from envctl.observability.models import ExecutionObservabilityContext

_ACTIVE_CONTEXT: ContextVar[ExecutionObservabilityContext | None] = ContextVar(
    "envctl_observability_context",
    default=None,
)


def set_active_context(context: ExecutionObservabilityContext | None) -> None:
    """Set active observability context for the current execution context."""

    _ACTIVE_CONTEXT.set(context)


def get_active_context() -> ExecutionObservabilityContext | None:
    """Return active observability context, if present."""

    return _ACTIVE_CONTEXT.get()


def clear_active_context() -> None:
    """Clear any active observability context."""

    _ACTIVE_CONTEXT.set(None)
