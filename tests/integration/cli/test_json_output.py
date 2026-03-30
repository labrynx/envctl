from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from envctl.cli.app import app


def parse_json_output(output: str) -> dict[str, Any]:
    """Parse one CLI JSON payload."""
    return cast(dict[str, Any], json.loads(output))


def test_check_json_outputs_structured_payload_for_invalid_environment(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "demo-app")

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["ok"] is False
    assert payload["command"] == "check"

    data = cast(dict[str, Any], payload["data"])
    assert data["context"]["project_slug"] == "repo"
    assert data["report"]["is_valid"] is False
    assert data["report"]["missing_required"] == ["DATABASE_URL"]
    assert data["report"]["unknown_keys"] == []
    assert data["report"]["invalid_keys"] == []


def test_check_json_outputs_success_payload_when_environment_is_valid(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "demo-app")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/app")

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "check"

    data = cast(dict[str, Any], payload["data"])
    assert data["report"]["is_valid"] is True
    assert data["report"]["missing_required"] == []
    assert sorted(data["report"]["values"]) == ["APP_NAME", "DATABASE_URL", "PORT"]


def test_inspect_json_outputs_structured_resolution_report(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "demo-app")

    result = runner.invoke(app, ["--json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "inspect"

    data = cast(dict[str, Any], payload["data"])
    assert data["context"]["project_slug"] == "repo"
    assert data["report"]["missing_required"] == ["DATABASE_URL"]
    assert "APP_NAME" in data["report"]["values"]
    assert data["report"]["values"]["APP_NAME"]["value"] == "demo-app"
    assert data["report"]["values"]["APP_NAME"]["source"] == "system"


def test_explain_json_outputs_one_resolved_item(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "demo-app")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/app")

    result = runner.invoke(app, ["--json", "explain", "DATABASE_URL"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "explain"

    data = cast(dict[str, Any], payload["data"])
    item = cast(dict[str, Any], data["item"])
    assert item["key"] == "DATABASE_URL"
    assert item["source"] == "system"
    assert item["masked"] is True
    assert item["valid"] is True
    assert str(item["value"]).startswith("po")


def test_explain_json_outputs_structured_error_for_unresolved_key(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "demo-app")

    result = runner.invoke(app, ["--json", "explain", "MISSING_KEY"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl explain",
        "error": {
            "type": "ValidationError",
            "message": "Key is not resolved: MISSING_KEY",
        },
    }


def test_status_json_outputs_structured_status_payload(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "status"

    data = cast(dict[str, Any], payload["data"])
    assert data["project_slug"] == "repo"
    assert data["contract_exists"] is True
    assert data["vault_exists"] is False
    assert data["resolved_valid"] is False
    assert isinstance(data["issues"], list)


def test_doctor_json_outputs_structured_checks(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "doctor"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "doctor"

    data = cast(dict[str, Any], payload["data"])
    assert "checks" in data
    assert isinstance(data["checks"], list)
    assert data["has_failures"] is False


def test_json_is_rejected_for_unsupported_text_only_command(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "vault", "show"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl vault show",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'vault show' yet.",
        },
    }
