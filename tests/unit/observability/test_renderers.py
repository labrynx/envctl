from __future__ import annotations

from envctl.observability.models import ObservationEvent
from envctl.observability.renderers import collect_top_slow_phases, render_profile_summary
from envctl.observability.timing import utcnow


def _event(name: str, status: str, duration_ms: int | None) -> ObservationEvent:
    return ObservationEvent(
        event=name,
        timestamp=utcnow(),
        execution_id="exec-1",
        status=status,
        duration_ms=duration_ms,
        module="tests",
        operation="test",
        fields={},
    )


def test_collect_top_slow_phases_aggregates_by_phase() -> None:
    phases = collect_top_slow_phases(
        [
            _event("context.resolve.finish", "finish", 10),
            _event("context.resolve.finish", "finish", 30),
            _event("run.exec.error", "error", 40),
            _event("context.resolve.start", "start", None),
        ]
    )

    assert [phase.phase for phase in phases] == ["run.exec", "context.resolve"]
    assert phases[1].count == 2
    assert phases[1].avg_duration_ms == 20


def test_render_profile_summary_lists_ranked_phases() -> None:
    output = render_profile_summary([
        _event("resolution.finish", "finish", 25),
        _event("profile.load.finish", "finish", 8),
    ])

    assert "Observability profile (top slow phases):" in output
    assert "resolution: max=25ms" in output
