from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_set_and_check_use_explicit_profile_file(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    runner.invoke(
        app, ["--profile", "staging", "set", "APP_NAME", "demo-staging"], catch_exceptions=False
    )
    runner.invoke(
        app,
        ["--profile", "staging", "set", "DATABASE_URL", "https://db.example.com"],
        catch_exceptions=False,
    )

    result = runner.invoke(
        app,
        ["--profile", "staging", "check"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "profile: staging" in result.stdout
