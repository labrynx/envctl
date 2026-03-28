from __future__ import annotations

import pytest
import typer

import envctl.cli.commands.check as check_command_module
from envctl.cli.commands.check import check_command
from envctl.domain.resolution import ResolutionReport


def test_check_command_exits_when_report_is_valid_but_unknown_keys_exist(monkeypatch) -> None:
    report = ResolutionReport(
        values={},
        missing_required=[],
        unknown_keys=["OLD_KEY"],
        invalid_keys=[],
    )
    captured: dict[str, str] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda: ("context", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "render_resolution",
        lambda _report: None,
    )
    monkeypatch.setattr(
        check_command_module,
        "print_warning",
        lambda message: captured.update({"warning": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1
    assert captured["warning"] == "Environment is valid, but the vault contains unknown keys"


def test_check_command_exits_when_report_is_invalid(monkeypatch) -> None:
    report = ResolutionReport(
        values={},
        missing_required=["APP_NAME"],
        unknown_keys=[],
        invalid_keys=[],
    )

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda: ("context", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "render_resolution",
        lambda _report: None,
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1
