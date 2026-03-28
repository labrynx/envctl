"""Repository removal service."""

from __future__ import annotations

from dataclasses import dataclass

from envctl.config.loader import load_config
from envctl.errors import LinkError
from envctl.models import ConfirmFn, ProjectContext
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


def _handle_repo_env(context: ProjectContext) -> tuple[bool, bool, bool]:
    """Handle repository .env.local removal or restoration.

    Returns:
        tuple[bool, bool, bool]:
            removed_repo_symlink,
            restored_repo_env_file,
            removed_broken_repo_symlink
    """
    removed_repo_symlink = False
    restored_repo_env_file = False
    removed_broken_repo_symlink = False

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

    return (
        removed_repo_symlink,
        restored_repo_env_file,
        removed_broken_repo_symlink,
    )


def run_remove(
    *,
    force: bool = False,
    confirm: ConfirmFn | None = None,
) -> RemoveResult:
    """Remove envctl management for the current repository.

    Args:
        force: Skip confirmation prompts.
        confirm: Function used to request confirmation from the caller.

    Raises:
        LinkError: If removal is aborted by the user.
    """
    config = load_config()
    context = require_project_context(config=config)

    if not force:
        if confirm is None:
            raise LinkError("Confirmation handler is required when force is false")

        confirmed = confirm(
            (
                f"Remove envctl management for project '{context.project_slug}'?\n"
                "This will remove repository metadata and delete the managed vault env file."
            ),
            False,
        )
        if not confirmed:
            raise LinkError("Remove aborted by user")

    removed_repo_symlink = False
    restored_repo_env_file = False
    removed_repo_metadata = False
    removed_vault_env = False
    removed_vault_project_dir = False
    left_regular_repo_env_untouched = False
    removed_broken_repo_symlink = False

    (
        removed_repo_symlink,
        restored_repo_env_file,
        removed_broken_repo_symlink,
    ) = _handle_repo_env(context)

    if not context.repo_env_path.is_symlink() and context.repo_env_path.exists():
        left_regular_repo_env_untouched = True

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
