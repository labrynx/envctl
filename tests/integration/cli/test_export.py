from __future__ import annotations

from typing import Any

import pytest
import typer

import envctl.cli.commands.export.command as export_command_module
from envctl.domain.selection import ContractSelection, group_selection


def _export_result(
    selection: ContractSelection | None,
) -> tuple[object, str, str, tuple[object, ...]]:
    return ("context", "prod", "export APP_NAME='demo'\n", ())


def test_export_command_uses_presenter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(export_command_module, "get_active_profile", lambda: "prod")
    monkeypatch.setattr(
        export_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )

    def fake_run_export(
        active_profile: str | None = None,
        format: str = "shell",
        selection: ContractSelection | None = None,
    ) -> tuple[object, str, str, tuple[object, ...]]:
        captured["selection"] = selection
        return _export_result(selection)

    monkeypatch.setattr(export_command_module, "run_export", fake_run_export)
    monkeypatch.setattr(export_command_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        export_command_module,
        "render_export_output",
        lambda *, profile, rendered: captured.update({"profile": profile, "rendered": rendered}),
    )

    export_command_module.export_command()

    selection = captured["selection"]
    assert isinstance(selection, ContractSelection)
    assert selection.describe() == "group=Application"
    assert captured["profile"] == "prod"
    assert captured["rendered"] == "export APP_NAME='demo'\n"


def test_export_command_rejects_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(export_command_module, "is_json_output", lambda: True)

    with pytest.raises(typer.Exit) as exc_info:
        export_command_module.export_command()

    assert exc_info.value.exit_code == 1
