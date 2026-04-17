from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import envctl.cli.commands.sync.command as sync_command_module
from envctl.domain.selection import ContractSelection, group_selection


def test_sync_command_calls_service_with_default_output_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(sync_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        sync_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )

    def fake_run_sync(
        active_profile: str | None = None,
        output_path: Path | None = None,
        selection: ContractSelection | None = None,
    ) -> tuple[object, str, Path, tuple[object, ...]]:
        captured.update(
            {
                "active_profile": active_profile,
                "output_path": output_path,
                "selection": selection,
            }
        )
        context = type("Ctx", (), {"repo_root": Path("/tmp/demo")})()
        return (context, "staging", Path("/tmp/demo/.env.staging"), ())

    monkeypatch.setattr("envctl.services.sync_service.run_sync", fake_run_sync)
    monkeypatch.setattr(
        sync_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    sync_command_module.sync_command(output_path=None)

    selection = captured["selection"]
    assert isinstance(selection, ContractSelection)
    assert captured["active_profile"] == "staging"
    assert captured["output_path"] is None
    assert selection.describe() == "group=Application"
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["profile"] == "staging"
    assert captured["output"].metadata["target"] == "/tmp/demo/.env.staging"
