from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import envctl.cli.commands.vault.commands.path as vault_path_module


def test_vault_path_command_prints_profile_and_path(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        vault_path_module,
        "run_vault_path",
        lambda profile: ("context", "staging", "/tmp/vault/profiles/staging.env"),
    )
    monkeypatch.setattr(
        vault_path_module,
        "get_active_profile",
        lambda: "staging",
    )

    vault_path_module.vault_path_command()

    output = capsys.readouterr().out
    assert "profile: staging" in output
    assert "vault_values: /tmp/vault/profiles/staging.env" in output
