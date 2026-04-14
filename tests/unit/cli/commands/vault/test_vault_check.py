from __future__ import annotations

from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.vault.commands.check as vault_check_module


def test_vault_check_command_exits_when_file_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": False,
            "parseable": False,
            "private_permissions": False,
            "key_count": 0,
            "path": "/tmp/vault/values.env",
            "state": "missing",
            "detail": "Vault file does not exist.",
        },
    )()

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_check",
        lambda profile=None: ("context", "local", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file does not exist" in output
    assert "vault_values: /tmp/vault/values.env" in output


def test_vault_check_command_exits_when_file_is_plaintext(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": True,
            "private_permissions": False,
            "key_count": 0,
            "path": "/tmp/vault/values.env",
            "state": "plaintext",
            "detail": "Run 'envctl vault encrypt' to migrate it.",
        },
    )()

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_check",
        lambda profile=None: ("context", "local", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file is plaintext" in output
    assert "state: plaintext" in output


def test_vault_check_command_succeeds_when_file_is_valid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": True,
            "private_permissions": True,
            "key_count": 3,
            "path": "/tmp/vault/values.env",
            "state": "encrypted",
            "detail": "Vault file is encrypted and readable.",
        },
    )()

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_check",
        lambda profile=None: ("context", "local", result),
    )

    vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert "[OK] Vault file is encrypted and readable" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "parseable: yes" in output
    assert "private_permissions: yes" in output
    assert "keys: 3" in output


def test_vault_check_command_exits_when_permissions_are_not_private(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = type(
        "Result",
        (),
        {
            "exists": True,
            "parseable": True,
            "private_permissions": False,
            "key_count": 2,
            "path": "/tmp/vault/values.env",
            "state": "encrypted",
            "detail": "Vault file is encrypted and readable.",
        },
    )()

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_check",
        lambda profile=None: ("context", "local", result),
    )

    with pytest.raises(typer.Exit) as exc:
        vault_check_module.vault_check_command()

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "private_permissions: no" in output
    assert "keys: 2" in output


def test_vault_check_command_rejects_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.runtime.get_command_path",
        lambda: "envctl vault check",
    )
    monkeypatch.setattr(
        "envctl.cli.serializers.common.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        vault_check_module.vault_check_command()

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload == {
        "ok": False,
        "command": "envctl vault check",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'vault check' yet.",
        },
    }
