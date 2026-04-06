from __future__ import annotations

from typing import Any, cast

import pytest

import envctl.cli.commands.doctor.command as doctor_command_module
from envctl.cli.commands.doctor import doctor_command
from envctl.domain.diagnostics import DiagnosticSummary, InspectResult
from envctl.domain.selection import ContractSelection
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def make_result() -> InspectResult:
    context = make_project_context(repo_root="/tmp/demo")
    return InspectResult(
        project=context,
        active_profile="staging",
        selection=ContractSelection(),
        contract_path=str(context.repo_contract_path),
        values_path=str(context.vault_values_path),
        summary=DiagnosticSummary(total=1, valid=1, invalid=0, unknown=0),
        variables=(make_resolved_value(key="APP_NAME", value="demo", source="vault"),),
        problems=(),
    )


def test_doctor_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    result = make_result()

    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda profile: (result.project, result, ()),
    )
    monkeypatch.setattr(doctor_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(doctor_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        doctor_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    doctor_command()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["command"] == "doctor"
    assert payload["data"]["runtime"]["active_profile"] == "staging"
    assert payload["data"]["warnings"]


def test_doctor_command_renders_alias_warning(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = make_result()
    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda profile: (result.project, result, ()),
    )
    monkeypatch.setattr(doctor_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(doctor_command_module, "is_json_output", lambda: False)

    doctor_command()

    output = capsys.readouterr().out
    assert "deprecated" in output
    assert "envctl inspect" in output
    assert "v2.6.0" in output


def test_doctor_command_json_warns_about_deprecation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    result = make_result()

    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda profile: (result.project, result, ()),
    )
    monkeypatch.setattr(doctor_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(doctor_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        doctor_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    doctor_command()

    payload = cast(dict[str, Any], captured["payload"])
    messages = [warning["message"] for warning in payload["data"]["warnings"]]
    assert any("envctl doctor" in message for message in messages)
    assert any("envctl inspect" in message for message in messages)
    assert any("v2.6.0" in message for message in messages)


def test_doctor_command_keeps_same_core_payload_as_inspect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    result = make_result()

    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda profile: (result.project, result, ()),
    )
    monkeypatch.setattr(doctor_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(doctor_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        doctor_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    doctor_command()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["data"]["project"]["project_slug"] == result.project.project_slug
    assert payload["data"]["summary"]["total"] == result.summary.total
    assert payload["data"]["variables"]["APP_NAME"]["value"] == "demo"
