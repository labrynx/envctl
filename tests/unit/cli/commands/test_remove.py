from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import envctl.cli.commands.remove.command as remove_command_module


def test_remove_command_prints_profile_cleanup_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        remove_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        remove_command_module,
        "plan_remove",
        lambda key, active_profile=None: (
            "context",
            type(
                "Plan",
                (),
                {
                    "declared_in_contract": True,
                    "present_in_local_profile": True,
                    "present_in_other_profiles": ("dev",),
                },
            )(),
        ),
    )
    monkeypatch.setattr(
        remove_command_module,
        "run_remove",
        lambda key, active_profile=None: (
            type("Context", (), {"repo_root": "/tmp/repo"})(),
            type(
                "Result",
                (),
                {
                    "repo_contract_path": "/tmp/repo/.envctl.yaml",
                    "removed_from_contract": True,
                    "inspected_profiles": ("local", "dev", "staging"),
                    "removed_from_profiles": ("local", "dev"),
                    "missing_from_profiles": ("staging",),
                    "affected_paths": ("/tmp/vault/values.env", "/tmp/vault/profiles/dev.env"),
                },
            )(),
        ),
    )

    remove_command_module.remove_command("APP_NAME", yes=True)

    output = capsys.readouterr().out
    assert "Removed 'APP_NAME' from contract and persisted profiles" in output
    assert "inspected_profiles: local, dev, staging" in output
    assert "removed_from_profiles: local, dev" in output
    assert "missing_from_profiles: staging" in output
