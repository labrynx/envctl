from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

import envctl.cli.commands.status.command as status_command_module
from envctl.cli.commands.status import status_command
from envctl.domain.status import StatusReport
from tests.support.paths import normalize_path_str


def test_status_command_renders_status_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = StatusReport(
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=Path("/tmp/demo"),
        contract_exists=True,
        vault_exists=False,
        resolved_valid=False,
        summary="The project contract is not satisfied yet.",
        issues=["Missing required keys: DATABASE_URL"],
        suggested_action="Run 'envctl fill'",
    )
    called: dict[str, Any] = {}

    monkeypatch.setattr(
        status_command_module,
        "run_status",
        lambda profile: ("staging", report),
    )
    monkeypatch.setattr(
        status_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        status_command_module,
        "render_status_view",
        lambda *, profile, report: called.update({"profile": profile, "report": report}),
    )
    monkeypatch.setattr(
        status_command_module,
        "is_json_output",
        lambda: False,
    )

    status_command()

    assert called["profile"] == "staging"
    assert called["report"] is report


def test_status_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = StatusReport(
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=Path("/tmp/demo"),
        contract_exists=True,
        vault_exists=False,
        resolved_valid=False,
        summary="The project contract is not satisfied yet.",
        issues=["Missing required keys: DATABASE_URL", "Unknown keys in vault: OLD_KEY"],
        suggested_action="Run 'envctl fill'",
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        status_command_module,
        "run_status",
        lambda profile: ("staging", report),
    )
    monkeypatch.setattr(
        status_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        status_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        status_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    status_command()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is True
    assert payload["command"] == "status"
    assert payload["data"]["active_profile"] == "staging"
    assert payload["data"]["project_slug"] == "demo"
    assert payload["data"]["project_id"] == "prj_aaaaaaaaaaaaaaaa"
    assert normalize_path_str(payload["data"]["repo_root"]) == "/tmp/demo"
    assert payload["data"]["contract_exists"] is True
    assert payload["data"]["vault_exists"] is False
    assert payload["data"]["resolved_valid"] is False
    assert payload["data"]["issues"] == [
        "Missing required keys: DATABASE_URL",
        "Unknown keys in vault: OLD_KEY",
    ]
    assert payload["data"]["suggested_action"] == "Run 'envctl fill'"
