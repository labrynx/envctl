from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import envctl.cli.commands.status.command as status_command_module
from envctl.domain.status import StatusIssue, StatusReport
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
        summary_kind="unsatisfied",
        issues=(StatusIssue(kind="missing_required", keys=("DATABASE_URL",)),),
        suggested_action_kind="fill_or_set_values",
    )
    called: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.status_service.run_status",
        lambda profile: ("staging", report),
    )
    monkeypatch.setattr(
        status_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        status_command_module,
        "present",
        lambda output, *, output_format: called.update(
            {"output": output, "output_format": output_format}
        ),
    )
    monkeypatch.setattr(
        status_command_module,
        "is_json_output",
        lambda: False,
    )

    status_command_module.status_command()

    assert called["output_format"] == "text"
    assert called["output"].metadata["active_profile"] == "staging"
    assert called["output"].metadata["project_slug"] == "demo"


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
        summary_kind="unsatisfied",
        issues=(
            StatusIssue(kind="missing_required", keys=("DATABASE_URL",)),
            StatusIssue(kind="unknown_keys", keys=("OLD_KEY",)),
        ),
        suggested_action_kind="fill_or_set_values",
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.status_service.run_status",
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
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    status_command_module.status_command()

    output = captured["output"]
    assert captured["output_format"] == "json"
    assert output.metadata["ok"] is False
    assert output.metadata["active_profile"] == "staging"
    assert output.metadata["project_slug"] == "demo"
    assert output.metadata["project_id"] == "prj_aaaaaaaaaaaaaaaa"
    assert normalize_path_str(output.metadata["repo_root"]) == "/tmp/demo"
    assert output.metadata["contract_exists"] is True
    assert output.metadata["vault_exists"] is False
    assert output.metadata["resolved_valid"] is False
    assert output.metadata["issues"] == [
        "Missing required keys: DATABASE_URL",
        "Unknown keys in vault: OLD_KEY",
    ]
    assert output.metadata["suggested_action"] == "Run 'envctl fill' or 'envctl set KEY VALUE'"
