"""Git repository helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from envctl.errors import ExecutionError, ProjectDetectionError


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the completed process."""
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ProjectDetectionError("git executable not found") from exc

    if check and completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise ProjectDetectionError(message)

    return completed


def resolve_repo_root() -> Path:
    """Resolve the current Git repository root."""
    completed = _run_git(["rev-parse", "--show-toplevel"])
    return Path(completed.stdout.strip()).resolve()


def get_repo_remote(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    completed = _run_git(["remote", "get-url", "origin"], cwd=repo_root, check=False)
    if completed.returncode != 0:
        return None

    value = completed.stdout.strip()
    return value or None


def get_local_git_config(repo_root: Path, key: str) -> str | None:
    """Return one local Git config value when present."""
    completed = _run_git(["config", "--local", "--get", key], cwd=repo_root, check=False)
    if completed.returncode != 0:
        return None

    value = completed.stdout.strip()
    return value or None


def set_local_git_config(repo_root: Path, key: str, value: str) -> None:
    """Persist one local Git config value."""
    completed = _run_git(
        ["config", "--local", key, value],
        cwd=repo_root,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "git config failed"
        raise ExecutionError(message)


def unset_local_git_config(repo_root: Path, key: str) -> None:
    """Remove one local Git config value when present."""
    completed = _run_git(
        ["config", "--local", "--unset", key],
        cwd=repo_root,
        check=False,
    )
    if completed.returncode not in {0, 5}:
        message = completed.stderr.strip() or completed.stdout.strip() or "git config failed"
        raise ExecutionError(message)