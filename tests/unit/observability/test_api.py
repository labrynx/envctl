from __future__ import annotations

from envctl.observability import (
    clear_observability_context,
    get_active_observability_context,
    initialize_observability_context,
)


def test_initialize_observability_context_is_noop_when_disabled(
    monkeypatch,
) -> None:
    clear_observability_context()
    monkeypatch.delenv("ENVCTL_OBSERVABILITY_TRACE", raising=False)

    context = initialize_observability_context(command_name="check")

    assert context is None
    assert get_active_observability_context() is None


def test_initialize_observability_context_sets_active_context_when_enabled(
    monkeypatch,
) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_FORMAT", "text")

    context = initialize_observability_context(command_name="check")

    assert context is not None
    assert context.command_name == "check"
    assert context.trace_enabled is True
    assert context.profile_observability is False
    assert context.trace_format == "human"
    assert context.trace_output == "stderr"
    assert context.trace_file is None
    assert context.events == []
    assert get_active_observability_context() == context


def test_initialize_observability_context_sets_profile_mode_when_enabled(
    monkeypatch,
) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_PROFILE", "1")

    context = initialize_observability_context(command_name="check")

    assert context is not None
    assert context.profile_observability is True


def test_initialize_observability_context_assigns_default_latest_file(
    monkeypatch,
    tmp_path,
) -> None:
    clear_observability_context()
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE", "true")
    monkeypatch.setenv("ENVCTL_OBSERVABILITY_TRACE_OUTPUT", "file")
    monkeypatch.chdir(tmp_path)

    context = initialize_observability_context(command_name="check")

    assert context is not None
    assert context.trace_file == tmp_path / ".envctl" / "observability" / "latest.jsonl"
