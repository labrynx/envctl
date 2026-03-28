"""Git repository helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from envctl.errors import ProjectDetectionError


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    """Run a git command and return stripped stdout."""
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ProjectDetectionError("git executable not found") from exc
    except subprocess.CalledProcessError as exc:
        raise ProjectDetectionError(exc.stderr.strip() or "git command failed") from exc
    return completed.stdout.strip()


def resolve_repo_root() -> Path:
    """Resolve the current Git repository root."""
    root = _run_git(["rev-parse", "--show-toplevel"])
    return Path(root).resolve()


def get_repo_remote(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    try:
        value = _run_git(["remote", "get-url", "origin"], cwd=repo_root)
    except ProjectDetectionError:
        return None
    return value or None
