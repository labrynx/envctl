"""Git-related helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from envctl.constants import GIT_DIRNAME
from envctl.errors import ProjectDetectionError


def detect_repo_root(start: Path) -> Path | None:
    """Walk up from a path until a git root is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / GIT_DIRNAME).exists():
            return candidate
    return None


def resolve_repo_root(start: Path | None = None) -> Path:
    """Resolve the repository root, falling back to the current directory."""
    origin = (start or Path.cwd()).resolve()
    return detect_repo_root(origin) or origin


def require_git_repo_root(start: Path | None = None) -> Path:
    """Resolve the git repository root or fail explicitly."""
    origin = (start or Path.cwd()).resolve()
    repo_root = detect_repo_root(origin)
    if repo_root is None:
        raise ProjectDetectionError("envctl init must be run inside a Git repository")
    return repo_root


def get_repo_remote_url(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    value = result.stdout.strip()
    return value or None
