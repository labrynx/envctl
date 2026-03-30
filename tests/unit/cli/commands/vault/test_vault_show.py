from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.vault.commands.show as vault_show_module


def test_vault_show_command_exits_when_file_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=False,
        path="/tmp/vault/values.env",
        values={},
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda: (context, result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file does not exist" in output
    assert "vault_values: /tmp/vault/values.env" in output


def test_vault_show_command_warns_when_file_is_empty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=True,
        path="/tmp/vault/values.env",
        values={},
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda: (context, result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "load_contract_optional",
        lambda path: None,
    )

    vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert "vault_values: /tmp/vault/values.env" in output
    assert "[WARN] Vault file is empty" in output


def test_vault_show_command_masks_sensitive_contract_values_and_unknown_values(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=True,
        path="/tmp/vault/values.env",
        values={
            "APP_NAME": "demo",
            "API_KEY": "super-secret",
            "UNKNOWN": "mystery-value",
        },
    )
    contract = SimpleNamespace(
        variables={
            "APP_NAME": SimpleNamespace(sensitive=False),
            "API_KEY": SimpleNamespace(sensitive=True),
        }
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda: (context, result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "load_contract_optional",
        lambda path: contract,
    )
    monkeypatch.setattr(
        vault_show_module,
        "mask_value",
        lambda value: f"<masked:{value}>",
    )

    vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert "vault_values: /tmp/vault/values.env" in output
    assert "Values:" in output
    assert "  APP_NAME=demo" in output
    assert "  API_KEY=<masked:super-secret>" in output
    assert "  UNKNOWN=<masked:mystery-value>" in output


def test_vault_show_command_prints_raw_values_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=True,
        path="/tmp/vault/values.env",
        values={
            "APP_NAME": "demo",
            "API_KEY": "super-secret",
        },
    )
    contract = SimpleNamespace(
        variables={
            "APP_NAME": SimpleNamespace(sensitive=False),
            "API_KEY": SimpleNamespace(sensitive=True),
        }
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda: (context, result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "load_contract_optional",
        lambda path: contract,
    )
    monkeypatch.setattr(
        vault_show_module,
        "mask_value",
        lambda value: "<masked>",
    )
    monkeypatch.setattr(
        vault_show_module,
        "typer_confirm",
        lambda message, default=False: True,
    )

    vault_show_module.vault_show_command(raw=True)

    output = capsys.readouterr().out
    assert "  APP_NAME=demo" in output
    assert "  API_KEY=super-secret" in output
    assert "<masked>" not in output


def test_vault_show_command_masks_all_values_when_contract_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=True,
        path="/tmp/vault/values.env",
        values={
            "APP_NAME": "demo",
            "PORT": "3000",
        },
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda: (context, result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "load_contract_optional",
        lambda path: None,
    )
    monkeypatch.setattr(
        vault_show_module,
        "mask_value",
        lambda value: f"<masked:{value}>",
    )

    vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert "  APP_NAME=<masked:demo>" in output
    assert "  PORT=<masked:3000>" in output


def test_vault_show_command_rejects_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl vault show",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        vault_show_module.vault_show_command(raw=False)

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload == {
        "ok": False,
        "command": "envctl vault show",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'vault show' yet.",
        },
    }
