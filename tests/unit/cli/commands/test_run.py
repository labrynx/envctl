from __future__ import annotations

import pytest
import typer

from envctl.cli.commands.run import run_command_cli


def test_run_command_exits_with_child_return_code(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.commands.run.command.run_command",
        lambda command: 7,
    )

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(["python", "-V"])

    assert exc_info.value.exit_code == 7
