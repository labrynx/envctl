from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from cryptography.fernet import Fernet
from typer.testing import CliRunner

import envctl.adapters.git as git_adapters
from envctl.cli.app import app
from envctl.vault_crypto import serialize_master_key_v1


def _git(repo_root: Path, *args: str) -> None:
    # Intentional in tests: use git from PATH against a temporary local repository.
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def _write_sample_contract(repo_root: Path) -> None:
    (repo_root / ".envctl.yaml").write_text(
        "version: 1\n"
        "variables:\n"
        "  APP_NAME:\n"
        "    type: string\n"
        "    required: true\n"
        "    sensitive: false\n",
        encoding="utf-8",
    )


def test_guard_secrets_fails_for_staged_master_key(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch,
) -> None:
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)

    config_home = home / ".config"
    config_home.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    _write_sample_contract(repo)

    monkeypatch.chdir(repo)

    config_result = runner.invoke(app, ["config", "init"], catch_exceptions=False)
    assert config_result.exit_code == 0

    init_result = runner.invoke(app, ["init", "--contract", "skip"], catch_exceptions=False)
    assert init_result.exit_code == 0

    leaked_path = repo / "renamed-secret.txt"
    leaked_path.write_bytes(serialize_master_key_v1(Fernet.generate_key()))
    _git(repo, "add", leaked_path.name)

    # The CLI integration autouse fixtures patch envctl.adapters.git._run_git
    # for fake repositories. This test uses a real Git repository and must
    # restore the real adapter implementation before invoking the CLI.
    importlib.reload(git_adapters)

    guard_result = runner.invoke(app, ["guard", "secrets"], catch_exceptions=False)

    assert guard_result.exit_code == 1

    combined_output = guard_result.stdout + guard_result.stderr
    assert "contains an envctl master key" in combined_output
    assert "git restore --staged" in combined_output
    assert "git restore --staged" in guard_result.stdout
