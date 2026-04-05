from __future__ import annotations

from dataclasses import replace

from envctl.adapters.git import set_local_git_config
from envctl.constants import (
    DEFAULT_KEY_FILENAME,
    DEFAULT_STATE_FILENAME,
    DEFAULT_VALUES_FILENAME,
    GIT_CONFIG_PROJECT_ID_KEY,
)
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.errors import StateError
from envctl.repository.state_repository import upsert_state
from envctl.services.error_diagnostics import StateDiagnostics
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_ids import is_valid_project_id
from envctl.utils.project_paths import build_vault_project_dir


def persist_project_binding(config: AppConfig, context: ProjectContext) -> ProjectContext:
    """Persist the current repo ↔ vault binding and refresh vault state metadata."""
    if not is_valid_project_id(context.project_id):
        raise StateError(
            f"Cannot persist a non-canonical project id: {context.project_id!r}",
            diagnostics=StateDiagnostics(
                category="non_canonical_project_id",
                path=context.vault_state_path,
                field="project_id",
                suggested_actions=("envctl project rebind",),
            ),
        )

    ensure_dir(config.projects_dir)

    vault_project_dir = build_vault_project_dir(
        context.project_slug,
        context.project_id,
        config.projects_dir,
    )
    ensure_dir(vault_project_dir)

    set_local_git_config(
        context.repo_root,
        GIT_CONFIG_PROJECT_ID_KEY,
        context.project_id,
    )

    state_path = vault_project_dir / DEFAULT_STATE_FILENAME
    upsert_state(
        state_path,
        project_slug=context.project_slug,
        project_key=context.project_key,
        project_id=context.project_id,
        repo_root=str(context.repo_root),
        git_remote=context.repo_remote,
    )

    return replace(
        context,
        binding_source="local",
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=state_path,
        vault_key_path=vault_project_dir / DEFAULT_KEY_FILENAME,
    )
