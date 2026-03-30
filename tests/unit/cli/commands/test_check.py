from __future__ import annotations

import pytest
import typer

import envctl.cli.commands.check.command as check_command_module
from envctl.cli.commands.check import check_command
from tests.support.builders import make_resolution_report
from tests.support.contexts import make_project_context


def test_check_command_exits_when_report_is_valid_but_unknown_keys_exist(monkeypatch) -> None:
    report = make_resolution_report(
        values={},
        missing_required=(),
        unknown_keys=("OLD_KEY",),
        invalid_keys=(),
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
    monkeypatch.setattr(
        check_command_module,
        "is_json_output",
        lambda: False,
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1
    assert captured["warning"] == "Environment is valid, but the vault contains unknown keys"


def test_check_command_exits_when_report_is_invalid(monkeypatch) -> None:
    report = make_resolution_report(
        values={},
        missing_required=("APP_NAME",),
        unknown_keys=(),
        invalid_keys=(),
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
    monkeypatch.setattr(
        check_command_module,
        "is_json_output",
        lambda: False,
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1


def test_check_command_emits_json_when_requested(monkeypatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=(),
        unknown_keys=(),
        invalid_keys=(),
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda: (context, report),
    )
    monkeypatch.setattr(
        check_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        check_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    check_command()

    payload = captured["payload"]
    assert payload["ok"] is True
    assert payload["command"] == "check"
    assert payload["data"]["context"]["project_slug"] == "demo"
    assert payload["data"]["report"]["is_valid"] is True


def test_check_command_emits_json_and_exits_when_invalid(monkeypatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=("DATABASE_URL",),
        unknown_keys=(),
        invalid_keys=(),
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda: (context, report),
    )
    monkeypatch.setattr(
        check_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        check_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1
    payload = captured["payload"]
    assert payload["ok"] is False
    assert payload["data"]["report"]["missing_required"] == ["DATABASE_URL"]
