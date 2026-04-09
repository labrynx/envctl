from __future__ import annotations

from pathlib import Path

from envctl.observability.models import ObservationEvent
from envctl.observability.renderers import render_event
from envctl.observability.timing import utcnow

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _event(name: str, status: str, duration_ms: int) -> ObservationEvent:
    return ObservationEvent(
        event=name,
        timestamp=utcnow(),
        execution_id="exec-snapshot",
        status=status,
        duration_ms=duration_ms,
        module="tests",
        operation="snapshot",
        fields={},
    )


def _snapshot(name: str) -> str:
    return (SNAPSHOT_DIR / name).read_text(encoding="utf-8")


def _render_trace(events: list[ObservationEvent]) -> str:
    return "\n".join(render_event(event, "human") for event in events)


def test_human_trace_snapshot_for_check_command() -> None:
    rendered = _render_trace(
        [
            _event("command.start", "start", 0),
            _event("context.resolve.finish", "finish", 7),
            _event("contract.compose.finish", "finish", 5),
            _event("resolution.finish", "finish", 9),
            _event("command.finish", "finish", 23),
        ]
    )

    assert rendered == _snapshot("check_trace.txt")


def test_human_trace_snapshot_for_run_command() -> None:
    rendered = _render_trace(
        [
            _event("command.start", "start", 0),
            _event("run.exec.start", "start", 0),
            _event("subprocess.exec.finish", "finish", 18),
            _event("run.exec.finish", "finish", 26),
            _event("command.finish", "finish", 27),
        ]
    )

    assert rendered == _snapshot("run_trace.txt")


def test_human_trace_snapshot_for_vault_audit_command() -> None:
    rendered = _render_trace(
        [
            _event("command.start", "start", 0),
            _event("vault.start", "start", 0),
            _event("vault.finish", "finish", 14),
            _event("command.finish", "finish", 15),
        ]
    )

    assert rendered == _snapshot("vault_audit_trace.txt")
