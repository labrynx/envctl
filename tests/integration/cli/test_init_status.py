from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_init_and_status(runner: CliRunner, workspace: Path) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    result = runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Initialized" in result.stdout

    status = runner.invoke(app, ["status"], catch_exceptions=False)
    assert status.exit_code == 0
    assert "Project:" in status.stdout
