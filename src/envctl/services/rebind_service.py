"""Rebind service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.adapters.git import get_local_git_config, resolve_repo_root
from envctl.config.loader import load_config
from envctl.constants import GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.operations import RebindResult
from envctl.domain.project import ProjectContext
from envctl.repository.project_context import (
    build_context_for_project_id,
    find_vault_dir_by_project_id,
    persist_project_binding,
)
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.project_ids import new_project_id


def _load_previous_values(
    projects_dir: Path,
    previous_project_id: str | None,
) -> dict[str, str]:
    """Load previous vault values when available."""
    if previous_project_id is None:
        return {}

    previous_vault_dir = find_vault_dir_by_project_id(projects_dir, previous_project_id)
    if previous_vault_dir is None:
        return {}

    values_path = previous_vault_dir / "values.env"
    if not values_path.exists():
        return {}

    return load_env_file(values_path)


def run_rebind(*, copy_values: bool = True) -> tuple[ProjectContext, RebindResult]:
    """Generate a new canonical project id and bind the current checkout to it."""
    config = load_config()
    repo_root = resolve_repo_root()
    previous_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)

    previous_values = _load_previous_values(config.projects_dir, previous_project_id)

    new_project_id_value = new_project_id()
    context = build_context_for_project_id(
        config,
        repo_root=repo_root,
        project_id=new_project_id_value,
        binding_source="local",
    )
    context = persist_project_binding(config, context)

    ensure_dir(context.vault_project_dir)
    ensure_file(context.vault_values_path, "")

    copied = False
    if copy_values and previous_values:
        write_text_atomic(context.vault_values_path, dump_env(previous_values))
        copied = True

    return context, RebindResult(
        previous_project_id=previous_project_id,
        new_project_id=new_project_id_value,
        copied_values=copied,
    )