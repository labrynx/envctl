from __future__ import annotations

import pytest
import typer

from envctl.cli.commands.doctor import doctor_command


def test_doctor_command_exits_with_code_1_when_failures_exist(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.commands.doctor.run_doctor",
        lambda: ["dummy-check"],
    )
    monkeypatch.setattr(
        "envctl.cli.commands.doctor.render_doctor_checks",
        lambda checks: True,
    )

    with pytest.raises(typer.Exit) as exc_info:
        doctor_command()

    assert exc_info.value.exit_code == 1


def test_doctor_command_returns_normally_when_no_failures_exist(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.commands.doctor.run_doctor",
        lambda: ["dummy-check"],
    )
    monkeypatch.setattr(
        "envctl.cli.commands.doctor.render_doctor_checks",
        lambda checks: False,
    )

    assert doctor_command() is None
