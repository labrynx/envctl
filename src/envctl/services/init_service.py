"""Init service."""

from __future__ import annotations

from envctl.domain.project import ProjectContext
from envctl.repository.state_repository import write_state
from envctl.services.context_service import load_project_context
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions


def run_init(project_name: str | None = None) -> ProjectContext:
    """Initialize the current project inside the local vault."""
    _config, context = load_project_context(project_name=project_name)

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    ensure_file(context.vault_values_path, "")
    ensure_private_file_permissions(context.vault_values_path)

    write_state(
        context.vault_state_path,
        project_slug=context.project_slug,
        project_id=context.project_id,
        repo_root=str(context.repo_root),
    )
    ensure_private_file_permissions(context.vault_state_path)

    return context
