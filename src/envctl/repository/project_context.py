"""Project context builders."""

from __future__ import annotations

from envctl.constants import DEFAULT_STATE_FILENAME, DEFAULT_VALUES_FILENAME
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.utils.git import resolve_repo_root
from envctl.utils.project_ids import build_project_id
from envctl.utils.project_names import resolve_project_name
from envctl.utils.project_paths import build_vault_project_dir


def build_project_context(config: AppConfig, project_name: str | None = None) -> ProjectContext:
    """Build a project context from the current repository state."""
    repo_root = resolve_repo_root()
    project_slug = resolve_project_name(repo_root, project_name)
    project_id = build_project_id(repo_root)
    vault_project_dir = build_vault_project_dir(project_slug, project_id, config.projects_dir)

    return ProjectContext(
        project_slug=project_slug,
        project_id=project_id,
        repo_root=repo_root,
        repo_env_path=repo_root / config.env_filename,
        repo_contract_path=repo_root / config.schema_filename,
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=vault_project_dir / DEFAULT_STATE_FILENAME,
    )
