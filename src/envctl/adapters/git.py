"""Git repository helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import cast

from envctl.domain.error_diagnostics import (
    RepositoryDiscoveryDiagnosticCategory,
    RepositoryDiscoveryDiagnostics,
)
from envctl.errors import ExecutionError, ProjectDetectionError


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    text: bool = True,
) -> str | bytes:
    """Run a git command and return stdout."""
    try:
        # Intentional: git is resolved from PATH for portability across environments.
        completed = subprocess.run(  # nosec  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=str(cwd) if cwd else None,
            check=check,
            capture_output=True,
            text=text,
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
        stdout = (exc.stdout or b"") if not text else (exc.stdout or "")
        stderr = (exc.stderr or b"") if not text else (exc.stderr or "")
        stdout_str = (
            stdout.decode("utf-8", errors="replace").strip()
            if isinstance(stdout, bytes)
            else stdout.strip()
        )
        stderr_str = (
            stderr.decode("utf-8", errors="replace").strip()
            if isinstance(stderr, bytes)
            else stderr.strip()
        )
        message = stderr_str or stdout_str or "git command failed"

        if not check:
            return b"" if not text else ""

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
                git_stdout=stdout_str or None,
                git_stderr=stderr_str or None,
                suggested_actions=(
                    ("run envctl inside a git repository",)
                    if category == "not_a_git_repository"
                    else ("check git repository access",)
                ),
            ),
        ) from exc

    if text:
        stdout = cast(str, completed.stdout)
        return stdout.strip()

    return cast(bytes, completed.stdout)


def resolve_repo_root() -> Path:
    """Resolve the current Git repository root."""
    return Path(str(_run_git(["rev-parse", "--show-toplevel"]))).resolve()


def is_git_repository(repo_root: Path) -> bool:
    """Return whether the given directory is a Git repository."""
    try:
        value = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=repo_root, check=False)
    except ProjectDetectionError:
        return False
    return str(value).strip() == "true"


def get_repo_remote(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    try:
        value = _run_git(["remote", "get-url", "origin"], cwd=repo_root, check=False)
    except ProjectDetectionError:
        return None

    return str(value) or None


def get_local_git_config(repo_root: Path, key: str) -> str | None:
    """Return one local Git config value when present."""
    value = _run_git(["config", "--local", "--get", key], cwd=repo_root, check=False)
    return str(value) or None


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


def list_staged_paths(repo_root: Path) -> tuple[Path, ...]:
    """Return staged paths from the Git index."""
    output = _run_git(
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        cwd=repo_root,
        text=False,
    )
    if not isinstance(output, bytes) or not output:
        return ()
    return tuple(
        Path(item.decode("utf-8", errors="surrogateescape"))
        for item in output.split(b"\x00")
        if item
    )


def read_staged_file(repo_root: Path, path: Path) -> bytes:
    """Return the staged blob content for one path."""
    try:
        output = _run_git(["show", f":{path.as_posix()}"], cwd=repo_root, text=False)
    except ProjectDetectionError as exc:
        raise ExecutionError(f"Could not read staged content for '{path}'.") from exc
    if not isinstance(output, bytes):
        raise ExecutionError(f"Could not read staged content for '{path}'.")
    return output
