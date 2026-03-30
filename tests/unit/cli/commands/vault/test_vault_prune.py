from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import envctl.cli.commands.vault.commands.prune as vault_prune_module


def test_vault_prune_command_warns_when_no_unknown_keys_exist(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        vault_prune_module,
        "get_unknown_vault_keys",
        lambda profile: ("context", "dev", "/tmp/vault/profiles/dev.env", ()),
    )
    monkeypatch.setattr(
        vault_prune_module,
        "get_active_profile",
        lambda: "dev",
    )

    vault_prune_module.vault_prune_command(yes=True)

    output = capsys.readouterr().out
    assert "profile: dev" in output
    assert "vault_values: /tmp/vault/profiles/dev.env" in output
    assert "No unknown keys were removed" in output


def test_vault_prune_command_prunes_active_profile(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        vault_prune_module,
        "get_unknown_vault_keys",
        lambda profile: ("context", "staging", "/tmp/vault/profiles/staging.env", ("OLD_KEY",)),
    )
    monkeypatch.setattr(
        vault_prune_module,
        "run_vault_prune",
        lambda profile: (
            "context",
            "staging",
            "/tmp/vault/profiles/staging.env",
            type("Result", (), {"removed_keys": ("OLD_KEY",), "kept_keys": 2})(),
        ),
    )
    monkeypatch.setattr(
        vault_prune_module,
        "get_active_profile",
        lambda: "staging",
    )

    vault_prune_module.vault_prune_command(yes=True)

    output = capsys.readouterr().out
    assert "profile: staging" in output
    assert "Removed 1 unknown key(s) from profile 'staging'" in output
    assert "removed_keys: OLD_KEY" in output
    assert "kept_keys: 2" in output
