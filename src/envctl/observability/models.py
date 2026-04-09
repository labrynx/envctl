"""Core observability models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from envctl.observability.emitters import ObservabilityEmitter

TraceFormat = Literal["json", "text"]


@dataclass(frozen=True)
class ObservationEvent:
    """Structured event emitted during one command execution."""

    event: str
    timestamp: datetime
    execution_id: str
    status: str
    duration_ms: int | None = None
    module: str | None = None
    operation: str | None = None
    fields: dict[str, Any] | None = None

    @property
    def name(self) -> str:
        """Backward-compatible event name alias."""
        return self.event

    @property
    def payload(self) -> dict[str, Any]:
        """Backward-compatible payload alias."""
        payload: dict[str, Any] = {
            "execution_id": self.execution_id,
            "status": self.status,
        }
        if self.duration_ms is not None:
            payload["duration_ms"] = self.duration_ms
        if self.module is not None:
            payload["module"] = self.module
        if self.operation is not None:
            payload["operation"] = self.operation
        payload["fields"] = self.fields or {}
        return payload


# Backward-compatible type alias for older imports.
ObservabilityEvent = ObservationEvent


@dataclass(frozen=True)
class ExecutionObservabilityContext:
    """Request-scoped observability data for a single CLI execution."""

    execution_id: str
    command_name: str
    trace_enabled: bool
    profile_observability: bool
    trace_format: TraceFormat
    start_time: datetime
    emitters: tuple[ObservabilityEmitter, ...]
    events: list[ObservationEvent] | None = None
