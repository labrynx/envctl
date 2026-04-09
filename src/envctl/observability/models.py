"""Core observability models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from envctl.observability.emitters import ObservabilityEmitter

TraceFormat = Literal["json", "text"]


@dataclass(frozen=True)
class ObservabilityEvent:
    """Structured event emitted during one command execution."""

    name: str
    payload: dict[str, Any]
    timestamp: datetime


@dataclass(frozen=True)
class ExecutionObservabilityContext:
    """Request-scoped observability data for a single CLI execution."""

    execution_id: str
    command_name: str
    trace_enabled: bool
    trace_format: TraceFormat
    start_time: datetime
    emitters: tuple[ObservabilityEmitter, ...]
    events: list[ObservabilityEvent] | None = None
