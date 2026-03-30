"""Unbind service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.git import (
    get_local_git_config,
    resolve_repo_root,
    unset_local_git_config,
)
from envctl.constants import GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.operations import UnbindResult


def run_unbind() -> tuple[Path, UnbindResult]:
    """Remove the local git binding for the current repository checkout."""
    repo_root = resolve_repo_root()
    previous_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)

    if previous_project_id is None:
        return repo_root, UnbindResult(
            removed=False,
            previous_project_id=None,
        )

    unset_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)

    return repo_root, UnbindResult(
        removed=True,
        previous_project_id=previous_project_id,
    )
