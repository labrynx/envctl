"""Remove command domain models."""

from __future__ import annotations

from dataclasses import dataclass

from envctl.domain.project import ProjectContext


@dataclass(frozen=True)
class RemoveResult:
    """Result of a remove operation."""

    context: ProjectContext
    removed_repo_symlink: bool
    restored_repo_env_file: bool
    removed_repo_metadata: bool
    removed_vault_env: bool
    removed_vault_project_dir: bool
    left_regular_repo_env_untouched: bool
    removed_broken_repo_symlink: bool
