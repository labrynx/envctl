"""Helpers for building project contexts."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.app_config import AppConfig
from envctl.domain.metadata import ProjectMetadata
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError
from envctl.repository.metadata_repository import read_project_metadata
from envctl.utils.git import require_git_repo_root, resolve_repo_root
from envctl.utils.project_ids import build_project_id
from envctl.utils.project_names import resolve_project_name, slugify_project_name
from envctl.utils.project_paths import build_vault_project_dir


def build_project_context(config: AppConfig, project_name: str | None) -> ProjectContext:
    """Build a project context from the current repository and project name."""
    repo_root = require_git_repo_root()
    project_slug = resolve_project_name(repo_root, project_name)
    project_id = build_project_id(repo_root)

    repo_metadata_path = repo_root / config.metadata_filename
    repo_env_path = repo_root / config.env_filename
    vault_project_dir = build_vault_project_dir(project_slug, project_id, config.projects_dir)
    vault_env_path = vault_project_dir / config.env_filename

    return ProjectContext(
        project_slug=project_slug,
        project_id=project_id,
        repo_root=repo_root,
        repo_metadata_path=repo_metadata_path,
        repo_env_path=repo_env_path,
        vault_project_dir=vault_project_dir,
        vault_env_path=vault_env_path,
    )


def build_context_from_metadata(
    config: AppConfig,
    repo_root: Path,
    metadata: ProjectMetadata | None,
) -> ProjectContext | None:
    """Build a project context from stored repository metadata."""
    if metadata is None:
        return None

    normalized_slug = slugify_project_name(metadata.project_slug)
    normalized_id = metadata.project_id.strip()
    env_filename = metadata.env_filename.strip()

    if not env_filename:
        return None

    repo_metadata_path = repo_root / config.metadata_filename
    repo_env_path = repo_root / env_filename
    vault_project_dir = build_vault_project_dir(normalized_slug, normalized_id, config.projects_dir)
    vault_env_path = vault_project_dir / env_filename

    return ProjectContext(
        project_slug=normalized_slug,
        project_id=normalized_id,
        repo_root=repo_root,
        repo_metadata_path=repo_metadata_path,
        repo_env_path=repo_env_path,
        vault_project_dir=vault_project_dir,
        vault_env_path=vault_env_path,
    )


def require_project_context(config: AppConfig) -> ProjectContext:
    """Return the stored project context or fail if the repository is not initialized."""
    repo_root = resolve_repo_root()
    metadata_path = repo_root / config.metadata_filename
    metadata = read_project_metadata(metadata_path)
    context = build_context_from_metadata(
        config=config,
        repo_root=repo_root,
        metadata=metadata,
    )

    if context is None:
        raise ProjectDetectionError(
            "Repository project is unknown. Run 'envctl init [PROJECT]' first."
        )

    return context
