from __future__ import annotations

from pathlib import Path

from envctl.observability import (
    clear_observability_context,
    get_active_observability_context,
    initialize_observability_context,
)
from envctl.observability.recorder import record_event


def _emit_demo_finish_event() -> None:
    context = get_active_observability_context()
    assert context is not None

    record_event(
        context,
        event="resolution.finish",
        status="finish",
        duration_ms=12,
        module="tests.observability",
        operation="demo",
        fields={"profile": "local"},
    )


def test_profile_mode_file_trace_writes_latest_jsonl(monkeypatch, tmp_path: Path) -> None:
    clear_observability_context()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_PROFILE", "1")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_OUTPUT", "file")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_FORMAT", "jsonl")

    context = initialize_observability_context(command_name="check")

    assert context is not None
    assert context.profile_observability is True

    _emit_demo_finish_event()

    expected_path = tmp_path / ".envctl" / "observability" / "latest.jsonl"
    assert context.trace_file == expected_path
    assert expected_path.exists()

    content = expected_path.read_text(encoding="utf-8")
    assert '"event": "resolution.finish"' in content
    assert '"status": "finish"' in content


def test_profile_mode_file_trace_writes_latest_txt(monkeypatch, tmp_path: Path) -> None:
    clear_observability_context()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_PROFILE", "1")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_OUTPUT", "file")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_FORMAT", "human")

    context = initialize_observability_context(command_name="check")

    assert context is not None
    assert context.profile_observability is True

    _emit_demo_finish_event()

    expected_path = tmp_path / ".envctl" / "observability" / "latest.txt"
    assert context.trace_file == expected_path
    assert expected_path.exists()

    content = expected_path.read_text(encoding="utf-8")
    assert "Execution ID:" in content
    assert "[12ms] resolution status=finish" in content
