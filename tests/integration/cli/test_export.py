from __future__ import annotations

from typing import Any

import pytest
from typer.testing import CliRunner

import envctl.cli.commands.export.command as export_command_module
from envctl.cli.app import app
from envctl.domain.selection import ContractSelection, group_selection


def _export_result() -> tuple[object, str, str, tuple[object, ...]]:
    return ("context", "prod", "export APP_NAME='demo'\n", ())


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
    ) -> tuple[object, str, str, tuple[object, ...]]:
        captured["active_profile"] = active_profile
        captured["format"] = format
        captured["selection"] = selection
        return _export_result()

    monkeypatch.setattr("envctl.cli.commands.export.command.run_export", fake_run_export)
    monkeypatch.setattr(
        "envctl.cli.commands.export.command.render_export_output",
        lambda *, profile, rendered: captured.update({"profile": profile, "rendered": rendered}),
    )

    export_command_module.export_command(format="shell")

    selection = captured["selection"]
    assert isinstance(selection, ContractSelection)
    assert selection.describe() == "group=Application"
    assert captured["active_profile"] == "prod"
    assert captured["format"] == "shell"
    assert captured["profile"] == "prod"
    assert captured["rendered"] == "export APP_NAME='demo'\n"


def test_export_command_rejects_json_mode() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--json", "export"])

    assert result.exit_code == 1
    assert "JSON output is not supported for 'export' yet." in result.output
