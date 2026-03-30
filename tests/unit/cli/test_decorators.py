from __future__ import annotations

from types import SimpleNamespace

import pytest
import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.domain.runtime import RuntimeMode
from envctl.errors import EnvctlError, ExecutionError


def test_handle_errors_returns_wrapped_result() -> None:
    @handle_errors
    def sample(value: int) -> int:
        return value + 1

    assert sample(4) == 5


def test_handle_errors_converts_envctl_error_to_exit(monkeypatch) -> None:
    captured: dict[str, str] = {}

    @handle_errors
    def sample() -> None:
        raise EnvctlError("boom")

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.print_error",
        lambda message: captured.update({"message": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["message"] == "Error: boom"


def test_handle_errors_emits_structured_json_when_enabled(monkeypatch) -> None:
    captured: dict[str, object] = {}

    @handle_errors
    def sample() -> None:
        raise EnvctlError("boom")

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl check",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["payload"] == {
        "ok": False,
        "command": "envctl check",
        "error": {
            "type": "EnvctlError",
            "message": "boom",
        },
    }


def test_text_output_only_allows_text_mode(monkeypatch) -> None:
    @text_output_only("export")
    def sample() -> str:
        return "ok"

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: False,
    )

    assert sample() == "ok"


def test_text_output_only_rejects_json_mode(monkeypatch) -> None:
    @text_output_only("export")
    def sample() -> None:
        return None

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )

    with pytest.raises(ExecutionError, match="JSON output is not supported"):
        sample()


def test_requires_writable_runtime_allows_local_mode(monkeypatch) -> None:
    @requires_writable_runtime("add")
    def sample() -> str:
        return "ok"

    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.LOCAL),
    )

    assert sample() == "ok"


def test_requires_writable_runtime_rejects_ci_mode(monkeypatch) -> None:
    @requires_writable_runtime("add")
    def sample() -> None:
        return None

    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )

    with pytest.raises(ExecutionError, match="CI read-only mode"):
        sample()
