"""Bind service."""

from __future__ import annotations

from envctl.adapters.git import get_local_git_config, resolve_repo_root
from envctl.config.loader import load_config
from envctl.constants import GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.operations import BindResult
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.repository.project_context import (
    build_context_for_project_id,
    find_vault_dir_by_project_id,
    persist_project_binding,
)
from envctl.utils.logging import get_logger
from envctl.utils.project_ids import is_valid_project_id

logger = get_logger(__name__)


def run_bind(project_id: str) -> tuple[ProjectContext, BindResult]:
    """Bind the current repository checkout to an existing canonical project id."""
    logger.debug("Validating bind request", extra={"project_id": project_id})
    if not is_valid_project_id(project_id):
        raise ExecutionError(f"Invalid canonical project id: {project_id!r}")

    config = load_config()
    repo_root = resolve_repo_root()
    logger.debug(
        "Resolved bind repository root",
        extra={"project_id": project_id, "repo_root": repo_root},
    )

    vault_dir = find_vault_dir_by_project_id(config.projects_dir, project_id)
    if vault_dir is None:
        raise ExecutionError(
            f"No vault exists for project id '{project_id}'. "
            "Use 'envctl repair --create-if-missing' or 'envctl init' to create a new one."
        )
    logger.debug(
        "Resolved bind vault directory",
        extra={"project_id": project_id, "vault_dir": vault_dir},
    )

    previous_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)
    context = build_context_for_project_id(
        config,
        repo_root=repo_root,
        project_id=project_id,
        binding_source="local",
    )
    context = persist_project_binding(config, context)
    logger.info(
        "Repository binding updated",
        extra={
            "project_id": project_id,
            "previous_project_id": previous_project_id or "-",
            "changed": previous_project_id != project_id,
        },
    )

    return context, BindResult(
        project_id=project_id,
        changed=previous_project_id != project_id,
    )
