from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from envctl.cli.app import app
from tests.support.profile_values import patch_loaded_profile_values


def parse_json_output(output: str) -> dict[str, Any]:
    """Parse one CLI JSON payload."""
    return cast(dict[str, Any], json.loads(output))


def test_add_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["add", "APP_NAME", "demo"])

    assert result.exit_code == 1
    assert "Command 'add' is not available in CI read-only mode." in result.output


def test_set_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["set", "APP_NAME", "demo"])

    assert result.exit_code == 1
    assert "Command 'set' is not available in CI read-only mode." in result.output


def test_remove_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["remove", "APP_NAME", "--yes"])

    assert result.exit_code == 1
    assert "Command 'remove' is not available in CI read-only mode." in result.output


def test_init_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "Command 'init' is not available in CI read-only mode." in result.output


def test_project_rebind_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["project", "rebind", "--yes"])

    assert result.exit_code == 1
    assert "Command 'project rebind' is not available in CI read-only mode." in result.output


def test_vault_edit_is_blocked_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["vault", "edit"])

    assert result.exit_code == 1
    assert "Command 'vault edit' is not available in CI read-only mode." in result.output


def test_add_is_blocked_in_ci_mode_json_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "add", "APP_NAME", "demo"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl add",
        "error": {
            "type": "ExecutionError",
            "message": "Command 'add' is not available in CI read-only mode.",
        },
    }


def test_sync_is_blocked_in_ci_mode_json_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "sync"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl sync",
        "error": {
            "type": "ExecutionError",
            "message": "Command 'sync' is not available in CI read-only mode.",
        },
    }


def test_check_is_allowed_in_ci_mode_json_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
        },
    )

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["command"] == "check"
    assert payload["data"]["report"]["missing_required"] == ["DATABASE_URL"]


def test_status_is_allowed_in_ci_mode_json_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "status"


def test_doctor_is_allowed_in_ci_mode_json_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "inspect"


def test_run_remains_allowed_in_ci_mode_text_output(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
            "DATABASE_URL": "postgres://user:pass@localhost:5432/app",
        },
    )

    output_path = workspace / "child-output.txt"

    script = (
        "from pathlib import Path; "
        "import os; "
        "output = os.getenv('APP_NAME', ''); "
        f"Path({str(output_path)!r}).write_text("
        "output, encoding='utf-8')"
    )

    result = runner.invoke(
        app,
        [
            "run",
            "python3",
            "-c",
            script,
        ],
    )

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "demo-app"
