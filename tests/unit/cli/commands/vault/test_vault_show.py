from __future__ import annotations

from types import SimpleNamespace

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
        path="/tmp/vault/profiles/staging.env",
        values={},
    )

    monkeypatch.setattr(
        vault_show_module,
        "run_vault_show",
        lambda profile: (context, "staging", result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "get_active_profile",
        lambda: "local",
    )

    with pytest.raises(typer.Exit) as exc:
        vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert exc.value.exit_code == 1
    assert "[WARN] Vault file does not exist" in output
    assert "profile: staging" in output
    assert "vault_values: /tmp/vault/profiles/staging.env" in output


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
        lambda profile: (context, "local", result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "get_active_profile",
        lambda: "local",
    )
    monkeypatch.setattr(
        vault_show_module,
        "load_contract_optional",
        lambda path: None,
    )

    vault_show_module.vault_show_command(raw=False)

    output = capsys.readouterr().out
    assert "profile: local" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "[WARN] Vault file is empty" in output


def test_vault_show_command_masks_sensitive_contract_values_and_unknown_values(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(repo_contract_path="/tmp/repo/.envctl.schema.yaml")
    result = SimpleNamespace(
        exists=True,
        path="/tmp/vault/profiles/dev.env",
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
        lambda profile: (context, "dev", result),
    )
    monkeypatch.setattr(
        vault_show_module,
        "get_active_profile",
        lambda: "local",
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
    assert "profile: dev" in output
    assert "vault_values: /tmp/vault/profiles/dev.env" in output
    assert "Values:" in output
    assert "  APP_NAME=demo" in output
    assert "  API_KEY=<masked:super-secret>" in output
    assert "  UNKNOWN=<masked:mystery-value>" in output
