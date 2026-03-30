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
) -> str:
    """Run a git command and return stripped stdout."""
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=check,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ProjectDetectionError("git executable not found") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or "").strip() or (exc.stdout or "").strip() or "git command failed"

        if not check:
            return ""

        raise ProjectDetectionError(message) from exc

    return completed.stdout.strip()


def resolve_repo_root() -> Path:
    """Resolve the current Git repository root."""
    return Path(_run_git(["rev-parse", "--show-toplevel"])).resolve()


def get_repo_remote(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    try:
        value = _run_git(["remote", "get-url", "origin"], cwd=repo_root, check=False)
    except ProjectDetectionError:
        return None

    return value or None


def get_local_git_config(repo_root: Path, key: str) -> str | None:
    """Return one local Git config value when present."""
    value = _run_git(["config", "--local", "--get", key], cwd=repo_root, check=False)
    return value or None


def set_local_git_config(repo_root: Path, key: str, value: str) -> None:
    """Persist one local Git config value."""
    try:
        _run_git(["config", "--local", key, value], cwd=repo_root, check=True)
    except ProjectDetectionError as exc:
        raise ExecutionError(str(exc)) from exc


def unset_local_git_config(repo_root: Path, key: str) -> None:
    """Remove one local Git config value when present."""
    try:
        _run_git(["config", "--local", "--unset", key], cwd=repo_root, check=True)
    except ProjectDetectionError as exc:
        message = str(exc).strip().lower()
        if "no such section or key" in message or "key does not contain a section" in message:
            return
        raise ExecutionError(str(exc)) from exc