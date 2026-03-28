"""Repository repair service."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from envctl.config.loader import load_config
from envctl.domain.project import ConfirmFn, ProjectContext
from envctl.errors import LinkError, ProjectDetectionError
from envctl.repository.project_context import require_project_context


def build_backup_path(repo_env_path: Path) -> Path:
    """Return a timestamped backup path for a conflicting repository env file."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return repo_env_path.with_name(f"{repo_env_path.name}.backup-{timestamp}")


def run_repair(
    *,
    force: bool = False,
    confirm: ConfirmFn | None = None,
) -> ProjectContext:
    """Repair the repository symlink using existing envctl metadata."""
    config = load_config()
    context = require_project_context(config=config)

    if not context.vault_env_path.exists():
        raise ProjectDetectionError(
            "Managed vault env file does not exist. "
            "Run 'envctl init' to initialize this repository."
        )

    if context.repo_env_path.is_symlink():
        current_target = context.repo_env_path.resolve()
        expected_target = context.vault_env_path.resolve()

        if current_target == expected_target:
            return context

        context.repo_env_path.unlink()
        context.repo_env_path.symlink_to(context.vault_env_path)
        return context

    if context.repo_env_path.exists():
        should_backup = True

        if not force:
            if confirm is None:
                raise LinkError("Confirmation handler is required when force is false")

            should_backup = confirm(
                (
                    f"A regular file already exists at '{context.repo_env_path}'. "
                    "Do you want to back it up and replace it with the managed symlink?"
                ),
                True,
            )

        if not should_backup:
            raise LinkError("Repair aborted by user")

        backup_path = build_backup_path(context.repo_env_path)
        context.repo_env_path.rename(backup_path)
        context.repo_env_path.symlink_to(context.vault_env_path)
        return context

    context.repo_env_path.symlink_to(context.vault_env_path)
    return context
