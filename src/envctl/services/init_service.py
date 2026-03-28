"""Project initialization service."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.constants import MANAGED_ENV_HEADER
from envctl.domain.project import ProjectContext
from envctl.errors import LinkError
from envctl.repository.metadata_repository import write_project_metadata
from envctl.repository.project_context import build_project_context
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.permissions import (
    ensure_private_dir_permissions,
    ensure_private_file_permissions,
)
from envctl.utils.project_ids import build_repo_fingerprint


def run_init(project_name: str | None = None) -> ProjectContext:
    """Initialize a project in the vault and persist repository metadata."""
    config = load_config()
    context = build_project_context(config=config, project_name=project_name)

    ensure_dir(config.vault_dir.parent)
    ensure_private_dir_permissions(config.vault_dir.parent)

    ensure_dir(config.vault_dir)
    ensure_private_dir_permissions(config.vault_dir)

    ensure_dir(config.projects_dir)
    ensure_private_dir_permissions(config.projects_dir)

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    ensure_file(context.vault_env_path, content=MANAGED_ENV_HEADER)
    ensure_private_file_permissions(context.vault_env_path)

    repo_fingerprint = build_repo_fingerprint(context.repo_root)
    write_project_metadata(
        context.repo_metadata_path,
        project_slug=context.project_slug,
        project_id=context.project_id,
        env_filename=config.env_filename,
        vault_project_dir=context.vault_project_dir,
        vault_env_path=context.vault_env_path,
        repo_fingerprint=repo_fingerprint,
    )

    if context.repo_env_path.exists() and not context.repo_env_path.is_symlink():
        raise LinkError(f"Refusing to overwrite regular file: {context.repo_env_path}")

    if context.repo_env_path.is_symlink():
        current_target = context.repo_env_path.resolve()
        expected_target = context.vault_env_path.resolve()
        if current_target == expected_target:
            return context
        raise LinkError(
            "Repository env link is inconsistent. Run 'envctl repair' to fix the local link."
        )

    context.repo_env_path.symlink_to(context.vault_env_path)
    return context
