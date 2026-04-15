from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app
from tests.support.paths import normalize_path_str


def test_profile_create_list_path_and_remove(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    created = runner.invoke(app, ["profile", "create", "dev"], catch_exceptions=False)
    assert created.exit_code == 0
    assert "Created profile 'dev'" in created.stdout

    listed = runner.invoke(app, ["profile", "list"], catch_exceptions=False)
    assert listed.exit_code == 0
    assert "local" in listed.stdout
    assert "dev" in listed.stdout

    path_result = runner.invoke(app, ["profile", "path", "dev"], catch_exceptions=False)
    assert path_result.exit_code == 0
    assert "profiles/dev.env" in normalize_path_str(path_result.stdout)

    removed = runner.invoke(app, ["profile", "remove", "dev", "--yes"], catch_exceptions=False)
    assert removed.exit_code == 0
    assert "Removed profile 'dev'" in removed.stdout


def test_explicit_profile_commands_fail_until_profile_is_created(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    set_result = runner.invoke(app, ["--profile", "staging", "set", "APP_NAME", "demo"])
    assert set_result.exit_code == 1
    assert "Create it with 'envctl profile create staging'" in set_result.output

    inspect_result = runner.invoke(app, ["--profile", "staging", "--json", "inspect"])
    assert inspect_result.exit_code == 1
    assert '"message": "Profile does not exist: staging. Create it with' in inspect_result.stdout
