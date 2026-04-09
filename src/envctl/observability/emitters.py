"""Emitter primitives for observability events."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

from envctl.observability.models import ObservationEvent, TraceFormat
from envctl.observability.renderers import render_event, render_execution_header


class ObservabilityEmitter(Protocol):
    """Protocol implemented by event emitters."""

    def emit(self, event: ObservationEvent) -> None:
        """Emit a single observability event."""


class NullEmitter:
    """Default no-op emitter used when tracing is disabled."""

    def emit(self, event: ObservationEvent) -> None:
        del event


class StreamEmitter:
    """Emit observability events to one writable stream."""

    def __init__(self, *, trace_format: TraceFormat, stream: object | None = None) -> None:
        self._trace_format = trace_format
        self._stream = stream if stream is not None else sys.stderr
        self._header_emitted = False

    def emit(self, event: ObservationEvent) -> None:
        if self._trace_format == "human" and not self._header_emitted:
            header = render_execution_header(
                execution_id=event.execution_id,
                started_at=event.timestamp,
                trace_format=self._trace_format,
            )
            if header:
                print(header, file=self._stream)
            self._header_emitted = True
        print(render_event(event, self._trace_format), file=self._stream)


class FileEmitter:
    """Emit observability events to one file, truncating on first event."""

    def __init__(self, *, path: Path, trace_format: TraceFormat) -> None:
        self._path = path
        self._trace_format = trace_format
        self._initialized = False

    def emit(self, event: ObservationEvent) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w" if not self._initialized else "a", encoding="utf-8") as handle:
            if self._trace_format == "human" and not self._initialized:
                header = render_execution_header(
                    execution_id=event.execution_id,
                    started_at=event.timestamp,
                    trace_format=self._trace_format,
                )
                if header:
                    handle.write(f"{header}\n")
            handle.write(f"{render_event(event, self._trace_format)}\n")
        self._initialized = True
