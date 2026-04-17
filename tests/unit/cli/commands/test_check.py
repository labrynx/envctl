from __future__ import annotations

from typing import Any

import pytest
import typer

import envctl.cli.commands.check.command as check_command_module
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
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.check_service.run_check",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(
        check_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )
    monkeypatch.setattr(check_command_module, "get_active_profile", lambda: "local")
    monkeypatch.setattr(
        check_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(check_command_module, "is_json_output", lambda: False)

    with pytest.raises(typer.Exit) as exc_info:
        check_command_module.check_command()

    assert exc_info.value.exit_code == 1
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["kind"] == "check"
    assert captured["output"].metadata["ok"] is False


def test_check_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_check_result(ok=True, profile="staging")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.check_service.run_check",
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
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    check_command_module.check_command()

    assert captured["output_format"] == "json"
    metadata = captured["output"].metadata
    assert metadata["ok"] is True
    assert metadata["active_profile"] == "staging"
    assert metadata["selection"] == {
        "mode": "group",
        "group": "Application",
        "set": None,
        "var": None,
    }
    assert metadata["summary"]["valid"] == 3


def test_check_command_emits_json_and_exits_when_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_check_result(ok=False)
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.check_service.run_check",
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
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        check_command_module.check_command()

    assert exc_info.value.exit_code == 1
    assert captured["output_format"] == "json"
    assert captured["output"].metadata["ok"] is False
    assert captured["output"].metadata["problems"][0]["key"] == "DATABASE_URL"
