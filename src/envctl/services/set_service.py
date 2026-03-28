"""Set environment variable in the managed vault env file."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError
from envctl.repository.project_context import require_project_context
from envctl.utils.dotenv import normalize_env_key, update_env_file_key, validate_env_value
from envctl.utils.permissions import ensure_private_file_permissions


def run_set(key: str, value: str) -> ProjectContext:
    """Create or update a key in the managed vault env file."""
    normalized_key = normalize_env_key(key)
    validate_env_value(value)

    config = load_config()
    context = require_project_context(config=config)

    if not context.vault_env_path.exists():
        raise ProjectDetectionError(
            "Managed vault env file does not exist. Run 'envctl repair' or 'envctl init'."
        )

    update_env_file_key(context.vault_env_path, key=normalized_key, value=value)
    ensure_private_file_permissions(context.vault_env_path)

    return context
