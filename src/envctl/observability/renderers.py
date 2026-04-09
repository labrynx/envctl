"""Rendering helpers for observability events."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from envctl.observability.models import ObservationEvent, TraceFormat


def render_event(event: ObservationEvent, trace_format: TraceFormat) -> str:
    """Render one event in the selected output format."""

    if trace_format == "human":
        phase_name = event.event.rsplit(".", 1)[0]
        if event.event.startswith("command.") and event.status in {"finish", "error"}:
            total_ms = event.duration_ms if event.duration_ms is not None else 0
            return f"Total [{total_ms}ms] status={event.status}"

        duration_ms = event.duration_ms if event.duration_ms is not None else 0
        return f"[{duration_ms}ms] {phase_name} status={event.status}"
    return json.dumps(
        {
            "timestamp": event.timestamp.isoformat(),
            "event": event.event,
            "execution_id": event.execution_id,
            "status": event.status,
            "duration_ms": event.duration_ms,
            "module": event.module,
            "operation": event.operation,
            "fields": event.fields or {},
        },
        sort_keys=True,
    )


def render_execution_header(
    *,
    execution_id: str,
    started_at: datetime,
    trace_format: TraceFormat,
) -> str:
    """Render execution-level header data."""

    if trace_format == "human":
        return f"Execution ID: {execution_id} at {started_at.isoformat()}"
    return ""


@dataclass(frozen=True)
class SlowPhase:
    """Aggregate timing stats for one phase."""

    phase: str
    count: int
    total_duration_ms: int
    max_duration_ms: int

    @property
    def avg_duration_ms(self) -> int:
        return int(self.total_duration_ms / self.count) if self.count else 0


def collect_top_slow_phases(events: list[ObservationEvent], *, top_n: int = 5) -> list[SlowPhase]:
    """Aggregate and rank the slowest observed phases from finish/error events."""

    aggregates: dict[str, dict[str, int]] = defaultdict(
        lambda: {"count": 0, "total_duration_ms": 0, "max_duration_ms": 0}
    )
    for event in events:
        if event.duration_ms is None:
            continue
        if event.status not in {"finish", "error"}:
            continue
        if not (event.event.endswith(".finish") or event.event.endswith(".error")):
            continue
        phase = event.event.rsplit(".", 1)[0]
        entry = aggregates[phase]
        entry["count"] += 1
        entry["total_duration_ms"] += event.duration_ms
        entry["max_duration_ms"] = max(entry["max_duration_ms"], event.duration_ms)

    ranked = [
        SlowPhase(
            phase=phase,
            count=stats["count"],
            total_duration_ms=stats["total_duration_ms"],
            max_duration_ms=stats["max_duration_ms"],
        )
        for phase, stats in aggregates.items()
    ]
    ranked.sort(key=lambda item: (item.max_duration_ms, item.total_duration_ms), reverse=True)
    return ranked[:top_n]


def render_profile_summary(events: list[ObservationEvent], *, top_n: int = 5) -> str:
    """Render an observability profile summary for diagnostics output."""

    top = collect_top_slow_phases(events, top_n=top_n)
    if not top:
        return "Observability profile: no timed phases were recorded."
    lines = ["Observability profile (top slow phases):"]
    for item in top:
        lines.append(
            f"- {item.phase}: max={item.max_duration_ms}ms "
            f"avg={item.avg_duration_ms}ms total={item.total_duration_ms}ms count={item.count}"
        )
    return "\n".join(lines)
