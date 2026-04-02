from __future__ import annotations

from pathlib import Path

import envctl.cli.commands.sync.command as sync_command_module


def test_sync_command_calls_service_with_default_output_path(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(sync_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        sync_command_module,
        "run_sync",
        lambda active_profile=None, output_path=None: captured.update(
            {"active_profile": active_profile, "output_path": output_path}
        )
        or ("context", "staging", Path("/tmp/demo/.env.staging")),
    )
    monkeypatch.setattr(
        sync_command_module,
        "render_sync_result",
        lambda *, profile, target_path: captured.update(
            {"profile": profile, "target_path": target_path}
        ),
    )

    sync_command_module.sync_command()

    assert captured["active_profile"] == "staging"
    assert captured["output_path"] is None
    assert captured["profile"] == "staging"
    assert captured["target_path"] == Path("/tmp/demo/.env.staging")


def test_sync_command_passes_custom_output_path(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}
    output_path = Path("/tmp/custom.env")

    monkeypatch.setattr(sync_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        sync_command_module,
        "run_sync",
        lambda active_profile=None, output_path=None: captured.update(
            {"active_profile": active_profile, "output_path": output_path}
        )
        or ("context", "staging", output_path),
    )
    monkeypatch.setattr(
        sync_command_module,
        "render_sync_result",
        lambda *, profile, target_path: captured.update(
            {"profile": profile, "target_path": target_path}
        ),
    )

    sync_command_module.sync_command(output=output_path)

    assert captured["active_profile"] == "staging"
    assert captured["output_path"] == output_path
    assert captured["profile"] == "staging"
    assert captured["target_path"] == output_path
