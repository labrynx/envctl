from __future__ import annotations

from typer.testing import CliRunner

from envctl.cli import app

runner = CliRunner()


def test_help_command() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "local environment vault manager" in result.stdout.lower()


def test_help_command_alias_runs() -> None:
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "local environment vault manager" in result.stdout.lower()


def test_help_command_alias_for_subcommand_runs() -> None:
    result = runner.invoke(app, ["help", "init"])
    assert result.exit_code == 0
    assert "initialize the current git repository" in result.stdout.lower()


def test_doctor_command_runs(isolated_env) -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "config:" in result.stdout
    assert "symlink_support" in result.stdout


def test_config_init_command_creates_config(isolated_env) -> None:
    result = runner.invoke(app, ["config", "init"])

    assert result.exit_code == 0
    assert "Created envctl config file" in result.stdout


def test_repair_command_runs_after_init(isolated_env, repo_dir, monkeypatch) -> None:
    from envctl.services.init_service import run_init

    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.repo_env_path.unlink()

    result = runner.invoke(app, ["repair"])
    assert result.exit_code == 0
    assert "Repaired project" in result.stdout
