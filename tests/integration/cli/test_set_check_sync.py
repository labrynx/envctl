from __future__ import annotations

from pathlib import Path

from envctl.cli.app import app


def test_check_fails_when_required_value_is_missing(runner, workspace: Path) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    result = runner.invoke(app, ["check"], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Missing required keys" in result.stdout


def test_set_check_and_sync(runner, workspace: Path) -> None:
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