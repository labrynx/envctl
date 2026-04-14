from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import envctl.cli.commands.profile.commands.copy as copy_module
import envctl.cli.commands.profile.commands.create as create_module
import envctl.cli.commands.profile.commands.list as list_module
import envctl.cli.commands.profile.commands.path as path_module
import envctl.cli.commands.profile.commands.remove as remove_module


def test_profile_list_command_prints_profiles(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "envctl.services.profile_service.run_profile_list",
        lambda active_profile: (
            "context",
            type(
                "Result",
                (),
                {
                    "active_profile": "staging",
                    "profiles": ("local", "dev", "staging"),
                },
            )(),
        ),
    )
    monkeypatch.setattr(list_module, "get_active_profile", lambda: "staging")

    list_module.profile_list_command()

    output = capsys.readouterr().out
    assert "active_profile: staging" in output
    assert "profiles: local, dev, staging" in output


def test_profile_create_command_prints_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "envctl.services.profile_service.run_profile_create",
        lambda profile: (
            "context",
            type(
                "Result",
                (),
                {
                    "profile": "dev",
                    "path": "/tmp/dev.env",
                    "created": True,
                },
            )(),
        ),
    )

    create_module.profile_create_command("dev")

    output = capsys.readouterr().out
    assert "Created profile 'dev'" in output
    assert "path: /tmp/dev.env" in output


def test_profile_copy_command_prints_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "envctl.services.profile_service.run_profile_copy",
        lambda source, target: (
            "context",
            type(
                "Result",
                (),
                {
                    "source_profile": "dev",
                    "target_profile": "staging",
                    "source_path": "/tmp/dev.env",
                    "target_path": "/tmp/staging.env",
                    "copied_keys": 2,
                },
            )(),
        ),
    )

    copy_module.profile_copy_command("dev", "staging")

    output = capsys.readouterr().out
    assert "Copied profile 'dev' into 'staging'" in output
    assert "copied_keys: 2" in output


def test_profile_remove_command_aborts_on_confirmation_reject(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(remove_module, "confirm", lambda message, default=False: False)

    remove_module.profile_remove_command("dev", yes=False)

    output = capsys.readouterr().out
    assert "Nothing was changed." in output


def test_profile_path_command_uses_argument_or_active_profile(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "envctl.services.profile_service.run_profile_path",
        lambda profile=None, active_profile=None: (
            "context",
            type(
                "Result",
                (),
                {
                    "profile": "staging",
                    "path": "/tmp/staging.env",
                },
            )(),
        ),
    )
    monkeypatch.setattr(path_module, "get_active_profile", lambda: "dev")

    path_module.profile_path_command("staging")

    output = capsys.readouterr().out
    assert "profile: staging" in output
    assert "path: /tmp/staging.env" in output
