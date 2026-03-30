from __future__ import annotations

import pytest
import typer

import envctl.cli.commands.vault.commands.check as vault_check_module


def test_vault_check_command_exits_when_file_does_not_exist(monkeypatch, capsys) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": False,
            "parseable": False,
            "private_permissions": False,
            "key_count": 0,
            "path": "/tmp/vault/values.env",
        },
    )()

    monkeypatch.setattr(
        vault_check_module,
        "run_vault_check",
        lambda: ("context", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file does not exist" in output
    assert "vault_values: /tmp/vault/values.env" in output


def test_vault_check_command_exits_when_file_is_not_parseable(monkeypatch, capsys) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": False,
            "private_permissions": False,
            "key_count": 0,
            "path": "/tmp/vault/values.env",
        },
    )()

    monkeypatch.setattr(
        vault_check_module,
        "run_vault_check",
        lambda: ("context", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file is not parseable" in output
    assert "vault_values: /tmp/vault/values.env" in output


def test_vault_check_command_succeeds_when_file_is_valid(monkeypatch, capsys) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": True,
            "private_permissions": True,
            "key_count": 3,
            "path": "/tmp/vault/values.env",
        },
    )()

    monkeypatch.setattr(
        vault_check_module,
        "run_vault_check",
        lambda: ("context", result),
    )

    vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert "[OK] Vault file looks valid" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "parseable: yes" in output
    assert "private_permissions: yes" in output
    assert "keys: 3" in output


def test_vault_check_command_exits_when_permissions_are_not_private(monkeypatch, capsys) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": True,
            "private_permissions": False,
            "key_count": 2,
            "path": "/tmp/vault/values.env",
        },
    )()

    monkeypatch.setattr(
        vault_check_module,
        "run_vault_check",
        lambda: ("context", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file is parseable but permissions are not private enough" in output
    assert "parseable: yes" in output
    assert "private_permissions: no" in output
    assert "keys: 2" in output


def test_vault_check_command_rejects_json_mode(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl vault check",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        vault_check_module.vault_check_command()

    assert exc_info.value.exit_code == 1
    assert captured["payload"] == {
        "ok": False,
        "command": "envctl vault check",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'vault check' yet.",
        },
    }