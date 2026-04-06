from __future__ import annotations

from types import SimpleNamespace

import pytest
import typer

import envctl.cli.commands.run.command as run_command_module
from envctl.cli.commands.run import run_command_cli
from envctl.domain.operations import RunCommandResult
from envctl.domain.selection import group_selection


def test_run_command_exits_with_child_return_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(run_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        run_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(
        run_command_module,
        "run_command",
        lambda command, profile, *, selection=None: (
            "context",
            RunCommandResult(
                active_profile="staging",
                exit_code=7,
                warnings=(),
            ),
            (),
        ),
    )
    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(SimpleNamespace(args=["python", "-V"]))

    assert exc_info.value.exit_code == 7


def test_run_command_rejects_json_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(SimpleNamespace(args=["python", "-V"]))

    assert exc_info.value.exit_code == 1
