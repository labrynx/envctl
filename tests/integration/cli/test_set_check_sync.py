from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from envctl.cli.app import app


def test_check_fails_when_required_value_is_missing(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    result = runner.invoke(app, ["check"], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Missing required keys" in result.stdout


def test_set_check_and_sync(runner: CliRunner, workspace: Path) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)
    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "PORT", "3000"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)

    check = runner.invoke(app, ["check"], catch_exceptions=False)
    assert check.exit_code == 0
    assert "Environment contract satisfied" in check.stdout

    sync = runner.invoke(app, ["sync"], catch_exceptions=False)
    assert sync.exit_code == 0
    assert "Synced generated environment" in sync.stdout


def test_check_fails_for_invalid_string_json_format(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    schema_path = workspace / ".envctl.schema.yaml"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    schema["variables"]["TEST_JSON"] = {
        "type": "string",
        "format": "json",
        "required": True,
        "sensitive": False,
    }
    schema_path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")

    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "PORT", "3000"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)
    runner.invoke(app, ["set", "TEST_JSON", '{\\"broken\\"}'], catch_exceptions=False)

    check = runner.invoke(app, ["check"], catch_exceptions=False)
    assert check.exit_code == 1
    assert "Invalid keys" in check.stdout
    assert "TEST_JSON: Expected a valid JSON string" in check.stdout


def test_add_format_json_persists_and_is_used_by_check(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "PORT", "3000"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)
    runner.invoke(
        app,
        ["add", "TEST_JSON", '{"ok": true}', "--type", "string", "--format", "json"],
        catch_exceptions=False,
    )

    schema = yaml.safe_load((workspace / ".envctl.schema.yaml").read_text(encoding="utf-8"))
    assert schema["variables"]["TEST_JSON"]["format"] == "json"

    runner.invoke(app, ["set", "TEST_JSON", '{\\"broken\\"}'], catch_exceptions=False)
    check = runner.invoke(app, ["check"], catch_exceptions=False)
    assert check.exit_code == 1
    assert "TEST_JSON: Expected a valid JSON string" in check.stdout
