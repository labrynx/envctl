"""Git repository helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from envctl.errors import ExecutionError, ProjectDetectionError
from envctl.services.error_diagnostics import (
    RepositoryDiscoveryDiagnosticCategory,
    RepositoryDiscoveryDiagnostics,
)


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
        raise ProjectDetectionError(
            "git executable not found",
            diagnostics=RepositoryDiscoveryDiagnostics(
                category="git_not_installed",
                repo_root=cwd,
                cwd=cwd,
                git_args=tuple(args),
                suggested_actions=("install git",),
            ),
        ) from exc
    except subprocess.CalledProcessError as exc:
        stdout = (exc.stdout or "").strip()
        stderr = (exc.stderr or "").strip()
        message = stderr or stdout or "git command failed"

        if not check:
            return ""

        category: RepositoryDiscoveryDiagnosticCategory = (
            "not_a_git_repository"
            if "not a git repository" in message.lower()
            else "git_command_failed"
        )
        raise ProjectDetectionError(
            message,
            diagnostics=RepositoryDiscoveryDiagnostics(
                category=category,
                repo_root=cwd,
                cwd=cwd,
                git_args=tuple(args),
                git_stdout=stdout or None,
                git_stderr=stderr or None,
                suggested_actions=(
                    ("run envctl inside a git repository",)
                    if category == "not_a_git_repository"
                    else ("check git repository access",)
                ),
            ),
        ) from exc

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
    existing = get_local_git_config(repo_root, key)
    if existing is None:
        return

    try:
        _run_git(["config", "--local", "--unset", key], cwd=repo_root, check=True)
    except ProjectDetectionError as exc:
        raise ExecutionError(str(exc)) from exc
