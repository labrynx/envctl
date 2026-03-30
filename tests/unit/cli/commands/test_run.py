from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.run.command as run_command_module
from envctl.cli.commands.run import run_command_cli
from envctl.domain.runtime import RuntimeMode


def test_run_command_exits_with_child_return_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        run_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        run_command_module,
        "run_command",
        lambda command, profile: ("context", "staging", 7),
    )

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(["python", "-V"])

    assert exc_info.value.exit_code == 7


def test_run_command_rejects_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl run",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(["python", "-V"])

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload == {
        "ok": False,
        "command": "envctl run",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'run' yet.",
        },
    }


def test_run_command_is_allowed_in_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        run_command_module,
        "get_active_profile",
        lambda: "ci",
    )
    monkeypatch.setattr(
        run_command_module,
        "run_command",
        lambda command, profile: ("context", "ci", 0),
    )

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(["python", "-V"])

    assert exc_info.value.exit_code == 0
