"""Set service."""

from __future__ import annotations

from envctl.domain.project import ProjectContext
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.dotenv import dump_env, load_env_file
from envctl.utils.filesystem import ensure_dir
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions


def run_set(key: str, value: str) -> ProjectContext:
    """Create or update one explicit key in the vault values file."""
    _config, context = load_project_context()

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    data = load_env_file(context.vault_values_path)
    data[key] = value

    write_text_atomic(context.vault_values_path, dump_env(data))
    ensure_private_file_permissions(context.vault_values_path)

    return context
