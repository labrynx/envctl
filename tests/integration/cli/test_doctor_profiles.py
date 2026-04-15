from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_doctor_reports_active_profile_in_json(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["profile", "create", "staging"], catch_exceptions=False)

    result = runner.invoke(app, ["--profile", "staging", "--json", "inspect"])

    assert result.exit_code == 0
    assert '"active_profile": "staging"' in result.stdout
