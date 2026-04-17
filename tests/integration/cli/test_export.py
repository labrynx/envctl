from __future__ import annotations

import json
from typing import Any

import pytest
from typer.testing import CliRunner

import envctl.cli.commands.export.command as export_command_module
from envctl.cli.app import app
from envctl.domain.selection import ContractSelection, group_selection


def _export_result() -> tuple[object, str, dict[str, str], str, tuple[object, ...]]:
    return ("context", "prod", {"APP_NAME": "demo"}, "export APP_NAME='demo'\n", ())


def test_export_command_uses_presenter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr("envctl.cli.commands.export.command.get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        "envctl.cli.commands.export.command.get_contract_selection",
        lambda: group_selection("Application"),
    )

    def fake_run_export(
        active_profile: str | None = None,
        format: str = "shell",
        selection: ContractSelection | None = None,
    ) -> tuple[object, str, dict[str, str], str, tuple[object, ...]]:
        captured["active_profile"] = active_profile
        captured["format"] = format
        captured["selection"] = selection
        return _export_result()

    monkeypatch.setattr("envctl.services.export_service.run_export", fake_run_export)
    monkeypatch.setattr(
        "envctl.cli.commands.export.command.present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    export_command_module.export_command(format="shell")

    selection = captured["selection"]
    assert isinstance(selection, ContractSelection)
    assert selection.describe() == "group=Application"
    assert captured["active_profile"] == "prod"
    assert captured["format"] == "shell"
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["active_profile"] == "prod"
    assert captured["output"].metadata["rendered"] == "export APP_NAME='demo'\n"


def test_export_command_emits_json_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    monkeypatch.setattr(
        "envctl.services.export_service.run_export",
        lambda *args, **kwargs: _export_result(),
    )

    result = runner.invoke(app, ["--output", "json", "export"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["metadata"]["kind"] == "export"
    assert payload["metadata"]["format"] == "shell"
    assert payload["metadata"]["values"]["APP_NAME"] == "demo"
