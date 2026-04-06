from __future__ import annotations

from typing import Any, cast

import pytest

import envctl.cli.commands.explain.command as explain_command_module
from envctl.cli.commands.explain import explain_command
from envctl.domain.diagnostics import InspectKeyResult
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def make_result() -> InspectKeyResult:
    context = make_project_context(repo_root="/tmp/demo")
    return InspectKeyResult(
        project=context,
        active_profile="staging",
        item=make_resolved_value(
            key="API_KEY",
            value="super-secret",
            source="vault",
            masked=True,
        ),
        contract_type="string",
        contract_format=None,
        groups=("Secrets",),
        default=None,
        sensitive=True,
    )


def test_explain_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = make_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key, profile: (result.project, result, ()),
    )
    monkeypatch.setattr(explain_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(explain_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        explain_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    explain_command("API_KEY")

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["command"] == "explain"
    assert payload["data"]["item"]["key"] == "API_KEY"
    assert payload["data"]["warnings"]


def test_explain_command_renders_alias_warning(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = make_result()
    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key, profile: (result.project, result, ()),
    )
    monkeypatch.setattr(explain_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(explain_command_module, "is_json_output", lambda: False)

    explain_command("API_KEY")

    output = capsys.readouterr().out
    assert "deprecated" in output
    assert "inspect KEY" in output
    assert "v2.6.0" in output


def test_explain_command_json_warns_about_deprecation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = make_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key, profile: (result.project, result, ()),
    )
    monkeypatch.setattr(explain_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(explain_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        explain_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    explain_command("API_KEY")

    payload = cast(dict[str, Any], captured["payload"])
    messages = [warning["message"] for warning in payload["data"]["warnings"]]
    assert any("envctl explain" in message for message in messages)
    assert any("inspect KEY" in message for message in messages)
    assert any("v2.6.0" in message for message in messages)


def test_explain_command_keeps_same_core_payload_as_inspect_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = make_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key, profile: (result.project, result, ()),
    )
    monkeypatch.setattr(explain_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(explain_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        explain_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    explain_command("API_KEY")

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["data"]["item"]["key"] == result.item.key
    assert payload["data"]["contract"]["type"] == result.contract_type
    assert payload["data"]["contract"]["groups"] == ["Secrets"]
