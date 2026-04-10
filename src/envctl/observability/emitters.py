"""Emitter primitives for observability events."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol, TextIO

from envctl.observability.models import ObservationEvent, SanitizationPolicy, TraceFormat
from envctl.observability.renderers import render_event, render_execution_header
from envctl.observability.sanitization import sanitize_event


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

    def __init__(
        self,
        *,
        trace_format: TraceFormat,
        stream: TextIO | None = None,
        sanitization_policy: SanitizationPolicy = "masked",
    ) -> None:
        self._trace_format = trace_format
        self._stream = stream
        self._sanitization_policy = sanitization_policy
        self._header_emitted = False
        self._command_started = False

    def emit(self, event: ObservationEvent) -> None:
        sanitized_event = sanitize_event(event, policy=self._sanitization_policy)
        stream = self._stream if self._stream is not None else sys.stderr
        if getattr(stream, "closed", False):
            return
        if self._trace_format == "human" and _should_skip_human_event(
            sanitized_event,
            command_started=self._command_started,
        ):
            if sanitized_event.event == "command.start":
                self._command_started = True
            return
        if self._trace_format == "human" and not self._header_emitted:
            header = render_execution_header(
                execution_id=sanitized_event.execution_id,
                started_at=sanitized_event.timestamp,
                trace_format=self._trace_format,
            )
            if header:
                print(header, file=stream)
            self._header_emitted = True
        rendered = render_event(sanitized_event, self._trace_format)
        if rendered:
            print(rendered, file=stream)
        if sanitized_event.event == "command.start":
            self._command_started = True


class FileEmitter:
    """Emit observability events to one file, truncating on first event."""

    def __init__(
        self,
        *,
        path: Path,
        trace_format: TraceFormat,
        sanitization_policy: SanitizationPolicy = "masked",
    ) -> None:
        self._path = path
        self._trace_format = trace_format
        self._sanitization_policy = sanitization_policy
        self._initialized = False
        self._command_started = False

    def emit(self, event: ObservationEvent) -> None:
        sanitized_event = sanitize_event(event, policy=self._sanitization_policy)
        if self._trace_format == "human" and _should_skip_human_event(
            sanitized_event,
            command_started=self._command_started,
        ):
            if sanitized_event.event == "command.start":
                self._command_started = True
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w" if not self._initialized else "a", encoding="utf-8") as handle:
            if self._trace_format == "human" and not self._initialized:
                header = render_execution_header(
                    execution_id=sanitized_event.execution_id,
                    started_at=sanitized_event.timestamp,
                    trace_format=self._trace_format,
                )
                if header:
                    handle.write(f"{header}\n")
            rendered = render_event(sanitized_event, self._trace_format)
            if rendered:
                handle.write(f"{rendered}\n")
        self._initialized = True
        if sanitized_event.event == "command.start":
            self._command_started = True


def _should_skip_human_event(
    event: ObservationEvent,
    *,
    command_started: bool,
) -> bool:
    """Hide repetitive startup phases after command lifecycle begins."""
    if not command_started:
        return False
    return event.operation in {"load_config", "resolve_active_profile"}
