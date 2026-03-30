from __future__ import annotations

import json

from envctl.cli.app import app


def parse_json_output(output: str) -> dict[str, object]:
    """Parse one CLI JSON payload."""
    return json.loads(output)


def test_add_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["add", "APP_NAME", "demo"])

    assert result.exit_code == 1
    assert "Command 'add' is not available in CI read-only mode." in result.output


def test_set_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["set", "APP_NAME", "demo"])

    assert result.exit_code == 1
    assert "Command 'set' is not available in CI read-only mode." in result.output


def test_remove_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["remove", "APP_NAME", "--yes"])

    assert result.exit_code == 1
    assert "Command 'remove' is not available in CI read-only mode." in result.output


def test_init_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "Command 'init' is not available in CI read-only mode." in result.output


def test_project_rebind_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["project", "rebind", "--yes"])

    assert result.exit_code == 1
    assert "Command 'project rebind' is not available in CI read-only mode." in result.output


def test_vault_edit_is_blocked_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["vault", "edit"])

    assert result.exit_code == 1
    assert "Command 'vault edit' is not available in CI read-only mode." in result.output


def test_add_is_blocked_in_ci_mode_json_output(
    runner,
    workspace,
    monkeypatch,
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
    runner,
    workspace,
    monkeypatch,
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
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")
    monkeypatch.setenv("APP_NAME", "demo-app")

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["command"] == "check"
    assert payload["data"]["report"]["missing_required"] == ["DATABASE_URL"]


def test_status_is_allowed_in_ci_mode_json_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "status"


def test_doctor_is_allowed_in_ci_mode_json_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")

    result = runner.invoke(app, ["--json", "doctor"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "doctor"


def test_run_remains_allowed_in_ci_mode_text_output(
    runner,
    workspace,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ENVCTL_RUNTIME_MODE", "ci")
    monkeypatch.setenv("APP_NAME", "demo-app")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/app")

    output_path = workspace / "child-output.txt"

    result = runner.invoke(
        app,
        [
            "run",
            "python3",
            "-c",
            (
                "from pathlib import Path; "
                "import os; "
                f"Path({str(output_path)!r}).write_text(os.getenv('APP_NAME', ''), encoding='utf-8')"
            ),
        ],
    )

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "demo-app"