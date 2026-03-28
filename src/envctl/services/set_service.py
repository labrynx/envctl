"""Set environment variable in the managed vault env file."""

from __future__ import annotations

import re

from envctl.config.loader import load_config
from envctl.errors import ProjectDetectionError, ValidationError
from envctl.models import ProjectContext
from envctl.utils.filesystem import update_env_file_key
from envctl.utils.paths import require_project_context
from envctl.utils.permissions import ensure_private_file_permissions

ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def run_set(key: str, value: str) -> ProjectContext:
    """Create or update a key in the managed vault env file.

    Behavior:
    - requires valid repository metadata
    - requires the managed vault env file to already exist
    - updates or inserts a dotenv-style `KEY=VALUE` entry
    - does not print the stored value
    - does not modify repository metadata
    - does not repair missing structure automatically

    TODO(v1.1):
    - support richer dotenv parsing and quoting preservation
    - support explicit empty-value workflows if needed
    - consider `--json` or machine-readable output modes
    """
    normalized_key = key.strip()

    if not normalized_key:
        raise ValidationError("Key cannot be empty")

    if not ENV_KEY_PATTERN.match(normalized_key):
        raise ValidationError(
            "Key must start with a letter or underscore "
            "and contain only letters, digits, or underscores"
        )

    if "\n" in value or "\r" in value:
        raise ValidationError("Value cannot contain newlines")

    config = load_config()
    context = require_project_context(config=config)

    if not context.vault_env_path.exists():
        raise ProjectDetectionError(
            "Managed vault env file does not exist. Run 'envctl repair' or 'envctl init'."
        )

    update_env_file_key(context.vault_env_path, key=normalized_key, value=value)
    ensure_private_file_permissions(context.vault_env_path)

    return context
