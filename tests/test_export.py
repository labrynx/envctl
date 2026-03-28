from __future__ import annotations

from pathlib import Path

from envctl.cli.app import app


def test_export_outputs_shell_lines(runner, workspace: Path) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init"], catch_exceptions=False)
    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)

    result = runner.invoke(app, ["export"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "export APP_NAME='demo'" in result.stdout
    assert "export DATABASE_URL='https://db.example.com'" in result.stdout
