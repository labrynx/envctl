from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import envctl.utils.git as git_utils
from envctl.errors import ProjectDetectionError
from envctl.utils.git import _run_git, get_repo_remote, resolve_repo_root


def test_run_git_returns_stripped_stdout(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        return SimpleNamespace(stdout="/tmp/repo\n")

    monkeypatch.setattr(git_utils.subprocess, "run", fake_run)

    result = _run_git(["rev-parse", "--show-toplevel"])

    assert result == "/tmp/repo"


def test_run_git_raises_when_git_executable_is_missing(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(git_utils.subprocess, "run", fake_run)

    with pytest.raises(ProjectDetectionError, match="git executable not found"):
        _run_git(["status"])


def test_run_git_raises_with_stderr_when_git_command_fails(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "status"],
            stderr="fatal: not a git repository\n",
        )

    monkeypatch.setattr(git_utils.subprocess, "run", fake_run)

    with pytest.raises(ProjectDetectionError, match="fatal: not a git repository"):
        _run_git(["status"])


def test_run_git_raises_generic_message_when_stderr_is_empty(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "status"],
            stderr="",
        )

    monkeypatch.setattr(git_utils.subprocess, "run", fake_run)

    with pytest.raises(ProjectDetectionError, match="git command failed"):
        _run_git(["status"])


def test_resolve_repo_root_returns_resolved_path(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(git_utils, "_run_git", lambda args, cwd=None: str(repo_root))

    result = resolve_repo_root()

    assert result == repo_root.resolve()


def test_get_repo_remote_returns_value_when_available(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(git_utils, "_run_git", lambda args, cwd=None: "git@github.com:alessbarb/envctl.git")

    result = get_repo_remote(repo_root)

    assert result == "git@github.com:alessbarb/envctl.git"


def test_get_repo_remote_returns_none_when_git_lookup_fails(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    def raise_detection_error(args, cwd=None):
        raise ProjectDetectionError("remote not found")

    monkeypatch.setattr(git_utils, "_run_git", raise_detection_error)

    result = get_repo_remote(repo_root)

    assert result is None


def test_get_repo_remote_returns_none_when_git_output_is_empty(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    monkeypatch.setattr(git_utils, "_run_git", lambda args, cwd=None: "")

    result = get_repo_remote(repo_root)

    assert result is None