"""Repository removal service."""

from __future__ import annotations

from dataclasses import dataclass

import typer

from envctl.config.loader import load_config
from envctl.errors import LinkError
from envctl.models import ProjectContext
from envctl.utils.filesystem import write_text_atomic
from envctl.utils.paths import require_project_context


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


def _handle_repo_env(context: ProjectContext) -> tuple[bool, bool, bool, bool]:
    """Handle the repository `.env.local` during remove.

    Returns a tuple with:
    - removed_repo_symlink
    - restored_repo_env_file
    - removed_broken_repo_symlink
    - left_regular_repo_env_untouched
    """
    removed_repo_symlink = False
    restored_repo_env_file = False
    removed_broken_repo_symlink = False
    left_regular_repo_env_untouched = False

    if context.repo_env_path.is_symlink():
        try:
            matches = context.repo_env_path.resolve() == context.vault_env_path.resolve()
        except OSError:
            matches = False

        if matches and context.vault_env_path.exists():
            content = context.vault_env_path.read_text(encoding="utf-8")
            context.repo_env_path.unlink()
            write_text_atomic(context.repo_env_path, content)
            removed_repo_symlink = True
            restored_repo_env_file = True
        else:
            context.repo_env_path.unlink()
            removed_repo_symlink = True
            removed_broken_repo_symlink = True
    elif context.repo_env_path.exists():
        left_regular_repo_env_untouched = True

    return (
        removed_repo_symlink,
        restored_repo_env_file,
        removed_broken_repo_symlink,
        left_regular_repo_env_untouched,
    )


def run_remove(force: bool = False) -> RemoveResult:
    """Remove envctl management for the current repository.

    Behavior:
    - requires valid repository metadata
    - prompts before destructive changes unless `force=True`
    - restores a real repository `.env.local` file from the managed vault file
      when the current repository symlink points to the expected managed vault file
    - removes repository metadata
    - removes the managed vault env file if present
    - removes the managed vault project directory if it becomes empty
    - never deletes or overwrites a regular repository `.env.local` file
    """
    config = load_config()
    context = require_project_context(config=config)

    if not force:
        confirmed = typer.confirm(
            (
                f"Remove envctl management for project '{context.project_slug}'?\n"
                "This will remove repository metadata and delete the managed vault env file."
            ),
            default=False,
        )
        if not confirmed:
            raise LinkError("Remove aborted by user")

    (
        removed_repo_symlink,
        restored_repo_env_file,
        removed_broken_repo_symlink,
        left_regular_repo_env_untouched,
    ) = _handle_repo_env(context)

    removed_repo_metadata = False
    removed_vault_env = False
    removed_vault_project_dir = False

    if context.repo_metadata_path.exists():
        context.repo_metadata_path.unlink()
        removed_repo_metadata = True

    if context.vault_env_path.exists():
        context.vault_env_path.unlink()
        removed_vault_env = True

    if context.vault_project_dir.exists():
        try:
            context.vault_project_dir.rmdir()
            removed_vault_project_dir = True
        except OSError:
            removed_vault_project_dir = False

    return RemoveResult(
        context=context,
        removed_repo_symlink=removed_repo_symlink,
        restored_repo_env_file=restored_repo_env_file,
        removed_repo_metadata=removed_repo_metadata,
        removed_vault_env=removed_vault_env,
        removed_vault_project_dir=removed_vault_project_dir,
        left_regular_repo_env_untouched=left_regular_repo_env_untouched,
        removed_broken_repo_symlink=removed_broken_repo_symlink,
    )
