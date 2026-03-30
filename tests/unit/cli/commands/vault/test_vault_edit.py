from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import envctl.cli.commands.vault.commands.edit as vault_edit_module


def test_vault_edit_command_prints_profile_and_path(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        vault_edit_module,
        "get_active_profile",
        lambda: "dev",
    )
    monkeypatch.setattr(
        vault_edit_module,
        "run_vault_edit",
        lambda profile: (
            "context",
            type(
                "Result",
                (),
                {
                    "created": True,
                    "profile": "staging",
                    "path": "/tmp/vault/profiles/staging.env",
                },
            )(),
        ),
    )

    vault_edit_module.vault_edit_command(profile="staging")

    output = capsys.readouterr().out
    assert "Created and opened profile 'staging' vault file" in output
    assert "profile: staging" in output
    assert "vault_values: /tmp/vault/profiles/staging.env" in output
