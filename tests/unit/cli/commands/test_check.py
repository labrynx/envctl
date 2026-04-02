from __future__ import annotations

from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.check.command as check_command_module
from envctl.cli.commands.check import check_command
from tests.support.builders import make_resolution_report
from tests.support.contexts import make_project_context


def test_check_command_exits_when_report_is_valid_but_unknown_keys_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
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
        lambda profile, *, group=None: (context, "staging", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "render_resolution_view",
        lambda *, profile, group, report: None,
    )
    monkeypatch.setattr(
        check_command_module,
        "print_warning",
        lambda message: captured.update({"warning": message}),
    )
    monkeypatch.setattr(
        check_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        check_command_module,
        "get_selected_group",
        lambda: "Application",
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


def test_check_command_exits_when_report_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=("APP_NAME",),
        unknown_keys=(),
        invalid_keys=(),
    )

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, group=None: (context, "local", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "render_resolution_view",
        lambda *, profile, group, report: None,
    )
    monkeypatch.setattr(
        check_command_module,
        "get_active_profile",
        lambda: "local",
    )
    monkeypatch.setattr(
        check_command_module,
        "get_selected_group",
        lambda: None,
    )
    monkeypatch.setattr(
        check_command_module,
        "is_json_output",
        lambda: False,
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1


def test_check_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=(),
        unknown_keys=(),
        invalid_keys=(),
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, group=None: (context, "staging", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        check_command_module,
        "get_selected_group",
        lambda: "Application",
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

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is True
    assert payload["command"] == "check"
    assert payload["data"]["active_profile"] == "staging"
    assert payload["data"]["selected_group"] == "Application"
    assert payload["data"]["context"]["project_slug"] == "demo"
    assert payload["data"]["report"]["is_valid"] is True


def test_check_command_emits_json_and_exits_when_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=("DATABASE_URL",),
        unknown_keys=(),
        invalid_keys=(),
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, group=None: (context, "local", report),
    )
    monkeypatch.setattr(
        check_command_module,
        "get_active_profile",
        lambda: "local",
    )
    monkeypatch.setattr(
        check_command_module,
        "get_selected_group",
        lambda: None,
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
    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is False
    assert payload["data"]["active_profile"] == "local"
    assert payload["data"]["report"]["missing_required"] == ["DATABASE_URL"]
