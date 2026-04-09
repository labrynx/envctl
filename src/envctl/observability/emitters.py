"""Emitter primitives for observability events."""

from __future__ import annotations

from typing import Protocol

from envctl.observability.models import ObservabilityEvent


class ObservabilityEmitter(Protocol):
    """Protocol implemented by event emitters."""

    def emit(self, event: ObservabilityEvent) -> None:
        """Emit a single observability event."""


class NullEmitter:
    """Default no-op emitter used when tracing is disabled."""

    def emit(self, event: ObservabilityEvent) -> None:
        del event
