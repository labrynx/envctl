from __future__ import annotations

from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.check.command as check_command_module
from envctl.cli.commands.check import check_command
from envctl.domain.diagnostics import CheckResult, DiagnosticProblem, DiagnosticSummary
from envctl.domain.selection import group_selection
from tests.support.contexts import make_project_context


def make_check_result(*, ok: bool, profile: str = "local") -> CheckResult:
    summary = DiagnosticSummary(
        total=3,
        valid=3 if ok else 1,
        invalid=0 if ok else 1,
        unknown=0,
    )
    problems: tuple[DiagnosticProblem, ...] = ()
    if not ok:
        problems = (
            DiagnosticProblem(
                key="DATABASE_URL",
                kind="missing_required",
                message="missing required value",
                actions=("envctl fill", "envctl set DATABASE_URL <value>"),
            ),
        )
    return CheckResult(
        active_profile=profile,
        selection=group_selection("Application"),
        summary=summary,
        problems=problems,
    )


def test_check_command_exits_when_result_is_not_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_check_result(ok=False)

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(check_command_module, "render_check_result", lambda result: None)
    monkeypatch.setattr(check_command_module, "get_active_profile", lambda: "local")
    monkeypatch.setattr(
        check_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(check_command_module, "is_json_output", lambda: False)

    with pytest.raises(typer.Exit) as exc_info:
        check_command()

    assert exc_info.value.exit_code == 1


def test_check_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_check_result(ok=True, profile="staging")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(check_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        check_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(check_command_module, "is_json_output", lambda: True)
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
    assert payload["data"]["selection"] == {
        "mode": "group",
        "group": "Application",
        "set": None,
        "var": None,
    }
    assert payload["data"]["summary"]["valid"] == 3


def test_check_command_emits_json_and_exits_when_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_check_result(ok=False)
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        check_command_module,
        "run_check",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(check_command_module, "get_active_profile", lambda: "local")
    monkeypatch.setattr(
        check_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(check_command_module, "is_json_output", lambda: True)
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
    assert payload["data"]["problems"][0]["key"] == "DATABASE_URL"
