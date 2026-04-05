from __future__ import annotations

from pathlib import Path

from envctl.constants import DEFAULT_KEY_FILENAME, DEFAULT_STATE_FILENAME, DEFAULT_VALUES_FILENAME
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.utils.project_paths import build_vault_project_dir


def build_context(
    *,
    config: AppConfig,
    repo_root: Path,
    repo_remote: str | None,
    repo_contract_path: Path,
    project_slug: str,
    project_key: str,
    project_id: str,
    binding_source: str,
    vault_project_dir: Path | None = None,
) -> ProjectContext:
    """Build a complete project context."""
    resolved_vault_project_dir = (
        vault_project_dir
        if vault_project_dir is not None
        else build_vault_project_dir(project_slug, project_id, config.projects_dir)
    )

    return ProjectContext(
        project_slug=project_slug,
        project_key=project_key,
        project_id=project_id,
        repo_root=repo_root,
        repo_remote=repo_remote,
        binding_source=binding_source,  # type: ignore[arg-type]
        repo_env_path=repo_root / config.env_filename,
        repo_contract_path=repo_contract_path,
        vault_project_dir=resolved_vault_project_dir,
        vault_values_path=resolved_vault_project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=resolved_vault_project_dir / DEFAULT_STATE_FILENAME,
        vault_key_path=resolved_vault_project_dir / DEFAULT_KEY_FILENAME,
    )
