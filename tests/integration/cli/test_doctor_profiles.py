from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_doctor_reports_active_profile_in_json(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--profile", "staging", "--json", "doctor"])

    assert result.exit_code == 0
    assert '"active_profile": "staging"' in result.stdout
