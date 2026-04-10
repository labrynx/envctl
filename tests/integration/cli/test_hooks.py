from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from envctl.cli.app import app
from tests.integration.cli.conftest import _git, _write_sample_contract


def _parse_json(output: str) -> dict[str, object]:
    return json.loads(output)


def test_hooks_install_status_remove_flow(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    install = runner.invoke(app, ["hooks", "install"], catch_exceptions=False)
    assert install.exit_code == 0
    assert (workspace / ".git" / "hooks" / "pre-commit").exists()
    assert (workspace / ".git" / "hooks" / "pre-push").exists()

    status = runner.invoke(app, ["hooks", "status"], catch_exceptions=False)
    assert status.exit_code == 0
    assert "Managed hooks are healthy" in status.stdout

    remove = runner.invoke(app, ["hooks", "remove"], catch_exceptions=False)
    assert remove.exit_code == 0

    status_after_remove = runner.invoke(app, ["hooks", "status"], catch_exceptions=False)
    assert status_after_remove.exit_code == 1


def test_hooks_status_json_reports_missing_hooks(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    result = runner.invoke(app, ["--json", "hooks", "status"], catch_exceptions=False)

    assert result.exit_code == 1
    payload = _parse_json(result.output)
    assert payload["ok"] is False
    assert payload["schema_version"] == 1
    assert payload["command"] == "hooks status"
    assert payload["data"]["overall_status"] == "degraded"


def test_hooks_install_without_force_keeps_foreign_hook_visible(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    hooks_path = workspace / ".git" / "hooks"
    hooks_path.mkdir(parents=True, exist_ok=True)
    (hooks_path / "pre-commit").write_text("#!/bin/sh\necho custom\n", encoding="utf-8")

    result = runner.invoke(app, ["hooks", "install"], catch_exceptions=False)

    assert result.exit_code == 1
    assert "conflicts" in result.stdout.lower()


def test_hooks_install_force_overwrites_foreign_hook(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    hooks_path = workspace / ".git" / "hooks"
    hooks_path.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_path / "pre-commit"
    hook_path.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")

    result = runner.invoke(app, ["hooks", "install", "--force"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "envctl hook-run pre-commit" in hook_path.read_text(encoding="utf-8")


def test_hook_wrapper_executes_via_sh_with_envctl_on_path(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch,
) -> None:
    if shutil.which("sh") is None:
        return

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

    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["hooks", "install"], catch_exceptions=False)

    safe_file = repo / "README.txt"
    safe_file.write_text("hello\n", encoding="utf-8")
    _git(repo, "add", safe_file.name)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shim_path = bin_dir / "envctl"
    shim_path.write_text(
        "#!/bin/sh\n"
        f'exec "{sys.executable}" -m envctl "$@"\n',
        encoding="utf-8",
    )
    shim_path.chmod(0o755)

    hook_path = repo / ".git" / "hooks" / "pre-commit"
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    result = subprocess.run(  # noqa: S603
        ["sh", str(hook_path)],  # noqa: S607
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "No staged envctl secrets detected" in result.stdout
