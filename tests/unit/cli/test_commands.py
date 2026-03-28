from __future__ import annotations

import typer
import pytest

from envctl.cli.commands.doctor import doctor_command
from envctl.cli.commands.explain import explain_command
from envctl.cli.commands.fill import fill_command
from envctl.cli.commands.inspect import inspect_command
from envctl.cli.commands.run import run_command_cli
from envctl.domain.resolution import ResolvedValue, ResolutionReport
from envctl.utils.masking import mask_value


def test_explain_command_outputs_detail_when_present(monkeypatch, capsys) -> None:
    item = ResolvedValue(
        key="PORT",
        value="abc",
        source="vault",
        masked=False,
        valid=False,
        detail="Expected an integer",
    )

    monkeypatch.setattr(
        "envctl.cli.commands.explain.run_explain",
        lambda key: ("context", item),
    )

    explain_command("PORT")

    captured = capsys.readouterr()
    output = captured.out

    assert "key: PORT" in output
    assert "source: vault" in output
    assert "value: abc" in output
    assert "valid: no" in output
    assert "detail: Expected an integer" in output


def test_explain_command_masks_sensitive_values(monkeypatch, capsys) -> None:
    item = ResolvedValue(
        key="API_KEY",
        value="super-secret",
        source="vault",
        masked=True,
        valid=True,
        detail=None,
    )

    monkeypatch.setattr(
        "envctl.cli.commands.explain.run_explain",
        lambda key: ("context", item),
    )

    explain_command("API_KEY")

    captured = capsys.readouterr()
    output = captured.out

    assert "key: API_KEY" in output
    assert f"value: {mask_value('super-secret')}" in output
    assert "valid: yes" in output
    assert "detail:" not in output


def test_fill_command_outputs_success_when_keys_are_changed(monkeypatch, capsys) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.cli.commands.fill.run_fill",
        lambda prompt: (context, ["API_KEY", "PORT"]),
    )

    fill_command()

    captured = capsys.readouterr()
    output = captured.out

    assert "Filled 2 key(s) for demo-project" in output
    assert "keys: API_KEY, PORT" in output


def test_fill_command_outputs_warning_when_nothing_changed(monkeypatch, capsys) -> None:
    context = type("Context", (), {"display_name": "demo-project"})()

    monkeypatch.setattr(
        "envctl.cli.commands.fill.run_fill",
        lambda prompt: (context, []),
    )

    fill_command()

    captured = capsys.readouterr()
    assert "No keys were changed" in captured.out


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


def test_inspect_command_renders_resolution(monkeypatch) -> None:
    report = ResolutionReport(
        values={},
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )
    called: dict[str, object] = {}

    monkeypatch.setattr(
        "envctl.cli.commands.inspect.run_inspect",
        lambda: ("context", report),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.inspect.render_resolution",
        lambda value: called.update({"report": value}),
    )

    inspect_command()

    assert called["report"] is report


def test_run_command_cli_exits_with_child_return_code(monkeypatch) -> None:
    monkeypatch.setattr(
        "envctl.cli.commands.run.run_command",
        lambda command: 7,
    )

    with pytest.raises(typer.Exit) as exc_info:
        run_command_cli(["python", "-V"])

    assert exc_info.value.exit_code == 7