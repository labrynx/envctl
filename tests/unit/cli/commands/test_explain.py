from __future__ import annotations

import envctl.cli.commands.explain.command as explain_command_module
from envctl.cli.commands.explain import explain_command
from envctl.utils.masking import mask_value
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def test_explain_command_outputs_detail_when_present(monkeypatch, capsys) -> None:
    item = make_resolved_value(
        key="PORT",
        value="abc",
        source="vault",
        masked=False,
        valid=False,
        detail="Expected an integer",
    )

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key: ("context", item),
    )
    monkeypatch.setattr(
        explain_command_module,
        "is_json_output",
        lambda: False,
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
    item = make_resolved_value(
        key="API_KEY",
        value="super-secret",
        source="vault",
        masked=True,
        valid=True,
        detail=None,
    )

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key: ("context", item),
    )
    monkeypatch.setattr(
        explain_command_module,
        "is_json_output",
        lambda: False,
    )

    explain_command("API_KEY")

    captured = capsys.readouterr()
    output = captured.out

    assert "key: API_KEY" in output
    assert f"value: {mask_value('super-secret')}" in output
    assert "valid: yes" in output
    assert "detail:" not in output


def test_explain_command_emits_json_when_requested(monkeypatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    item = make_resolved_value(
        key="API_KEY",
        value="super-secret",
        source="vault",
        masked=True,
        valid=True,
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        explain_command_module,
        "run_explain",
        lambda key: (context, item),
    )
    monkeypatch.setattr(
        explain_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        explain_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    explain_command("API_KEY")

    payload = captured["payload"]
    assert payload["ok"] is True
    assert payload["command"] == "explain"
    assert payload["data"]["context"]["project_slug"] == "demo"
    assert payload["data"]["item"]["key"] == "API_KEY"
    assert payload["data"]["item"]["masked"] is True
