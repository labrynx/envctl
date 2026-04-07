from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import envctl.adapters.git as git_adapters
from envctl.errors import ProjectDetectionError
from tests.support.assertions import require_repository_discovery_diagnostics


def test_run_git_returns_stripped_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(stdout="/tmp/repo\n")

    monkeypatch.setattr("envctl.adapters.git.subprocess.run", fake_run)

    result = git_adapters._run_git(["rev-parse", "--show-toplevel"])

    assert result == "/tmp/repo"


def test_run_git_raises_when_git_executable_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*args: Any, **_kwargs: Any) -> SimpleNamespace:
        raise FileNotFoundError("git not found")

    monkeypatch.setattr("envctl.adapters.git.subprocess.run", fake_run)

    with pytest.raises(ProjectDetectionError, match=r"git executable not found") as exc_info:
        git_adapters._run_git(["status"])

    diagnostics = require_repository_discovery_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "git_not_installed"


def test_run_git_raises_with_stderr_when_git_command_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*args: Any, **_kwargs: Any) -> SimpleNamespace:
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "status"],
            stderr="fatal: not a git repository\n",
        )

    monkeypatch.setattr("envctl.adapters.git.subprocess.run", fake_run)

    with pytest.raises(ProjectDetectionError, match=r"fatal: not a git repository") as exc_info:
        git_adapters._run_git(["status"])

    diagnostics = require_repository_discovery_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "not_a_git_repository"
    assert diagnostics.git_stderr == "fatal: not a git repository"


def test_run_git_raises_generic_message_when_stderr_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*args: Any, **_kwargs: Any) -> SimpleNamespace:
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "status"],
            stderr="",
        )

    monkeypatch.setattr("envctl.adapters.git.subprocess.run", fake_run)

    with pytest.raises(ProjectDetectionError, match=r"git command failed") as exc_info:
        git_adapters._run_git(["status"])

    diagnostics = require_repository_discovery_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "git_command_failed"


def test_resolve_repo_root_returns_resolved_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(
        git_adapters,
        "_run_git",
        lambda args, cwd=None, check=True: str(repo_root),
    )

    result = git_adapters.resolve_repo_root()

    assert result == repo_root.resolve()


def test_get_repo_remote_returns_value_when_available(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(
        git_adapters,
        "_run_git",
        lambda args, cwd=None, check=True: "git@github.com:labrynx/envctl.git",
    )

    result = git_adapters.get_repo_remote(repo_root)

    assert result == "git@github.com:labrynx/envctl.git"


def test_get_repo_remote_returns_none_when_git_lookup_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    def raise_detection_error(
        args: list[str],
        cwd: Path | None = None,
        check: bool = True,
    ) -> str:
        del cwd, check
        raise ProjectDetectionError("remote not found")

    monkeypatch.setattr(git_adapters, "_run_git", raise_detection_error)

    result = git_adapters.get_repo_remote(repo_root)

    assert result is None


def test_get_repo_remote_returns_none_when_git_output_is_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(git_adapters, "_run_git", lambda args, cwd=None, check=True: "")

    result = git_adapters.get_repo_remote(repo_root)

    assert result is None
