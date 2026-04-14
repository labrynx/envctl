from __future__ import annotations

from typing import Any

import pytest

import envctl.cli.commands.export.command as export_command_module
from envctl.domain.selection import ContractSelection, group_selection


def _export_result(
    selection: ContractSelection | None,
) -> tuple[object, str, dict[str, str], str, tuple[object, ...]]:
    return ("context", "prod", {"APP_NAME": "demo"}, "export APP_NAME='demo'\n", ())


def test_export_command_uses_presenter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr("envctl.cli.commands.export.command.get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        export_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )

    def fake_run_export(
        active_profile: str | None = None,
        format: str = "shell",
        selection: ContractSelection | None = None,
    ) -> tuple[object, str, dict[str, str], str, tuple[object, ...]]:
        captured["selection"] = selection
        return _export_result(selection)

    monkeypatch.setattr("envctl.services.export_service.run_export", fake_run_export)
    monkeypatch.setattr(
        export_command_module,
        "render_export_output",
        lambda *, profile, rendered: captured.update({"profile": profile, "rendered": rendered}),
    )

    export_command_module.export_command(format="shell")

    selection = captured["selection"]
    assert isinstance(selection, ContractSelection)
    assert selection.describe() == "group=Application"
    assert captured["rendered"] == "export APP_NAME='demo'\n"


def test_export_command_emits_json_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(export_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(export_command_module, "get_contract_selection", lambda: None)
    monkeypatch.setattr(
        "envctl.services.export_service.run_export",
        lambda *args, **kwargs: _export_result(None),
    )
    monkeypatch.setattr(
        export_command_module,
        "emit_json",
        lambda payload: captured.update(payload),
    )

    export_command_module.export_command(format="shell")

    assert captured["ok"] is True
    assert captured["command"] == "export"
    assert captured["data"]["active_profile"] == "prod"
    assert captured["data"]["format"] == "shell"
    assert captured["data"]["values"] == {"APP_NAME": "demo"}
    assert captured["data"]["rendered"] == "export APP_NAME='demo'\n"
