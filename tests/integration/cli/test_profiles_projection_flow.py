from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app


def test_sync_and_export_use_explicit_profile_values(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    runner.invoke(
        app,
        ["--profile", "staging", "set", "APP_NAME", "demo-staging"],
        catch_exceptions=False,
    )
    runner.invoke(
        app,
        ["--profile", "staging", "set", "PORT", "3000"],
        catch_exceptions=False,
    )
    runner.invoke(
        app,
        ["--profile", "staging", "set", "DATABASE_URL", "https://db.example.com"],
        catch_exceptions=False,
    )

    sync = runner.invoke(app, ["--profile", "staging", "sync"], catch_exceptions=False)
    assert sync.exit_code == 0
    assert "profile: staging" in sync.stdout

    env_file = workspace / ".env.local"
    assert env_file.exists()
    content = env_file.read_text(encoding="utf-8")
    assert "APP_NAME=demo-staging" in content
    assert "PORT=3000" in content
    assert "DATABASE_URL=https://db.example.com" in content

    export = runner.invoke(app, ["--profile", "staging", "export"], catch_exceptions=False)
    assert export.exit_code == 0
    assert "profile: staging" in export.stdout
    assert "export APP_NAME='demo-staging'" in export.stdout


def test_run_uses_explicit_profile_values(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    runner.invoke(
        app,
        ["--profile", "dev", "set", "APP_NAME", "demo-dev"],
        catch_exceptions=False,
    )
    runner.invoke(
        app,
        ["--profile", "dev", "set", "DATABASE_URL", "postgres://user:pass@localhost:5432/app"],
        catch_exceptions=False,
    )

    output_path = workspace / "profile-run.txt"
    script = (
        "from pathlib import Path; "
        "import os; "
        f"Path({str(output_path)!r}).write_text("
        "os.getenv('APP_NAME', ''), encoding='utf-8')"
    )

    result = runner.invoke(
        app,
        ["--profile", "dev", "run", "python3", "-c", script],
    )

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "demo-dev"
