from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_config_init(runner: CliRunner, workspace: Path) -> None:
    result = runner.invoke(app, ["config", "init"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Created envctl config file" in result.stdout
