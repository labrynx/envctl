"""Project context serializers."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.common import path_to_str
from envctl.domain.project import ProjectContext


def serialize_project_context(context: ProjectContext) -> dict[str, Any]:
    """Serialize one project context."""
    return {
        "project_slug": context.project_slug,
        "project_key": context.project_key,
        "project_id": context.project_id,
        "display_name": context.display_name,
        "repo_root": path_to_str(context.repo_root),
        "repo_remote": context.repo_remote,
        "binding_source": context.binding_source,
        "repo_env_path": path_to_str(context.repo_env_path),
        "repo_contract_path": path_to_str(context.repo_contract_path),
        "vault_project_dir": path_to_str(context.vault_project_dir),
        "vault_values_path": path_to_str(context.vault_values_path),
        "vault_state_path": path_to_str(context.vault_state_path),
    }
