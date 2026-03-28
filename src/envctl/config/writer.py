"""Config file writer helpers."""

from __future__ import annotations

from pathlib import Path

from envctl.config.defaults import (
    get_default_config_path,
    get_default_env_filename,
    get_default_vault_dir,
)
from envctl.errors import ConfigError
from envctl.utils.atomic import write_json_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.permissions import ensure_private_file_permissions
from envctl.utils.tilde import to_tilde_path


def write_default_config_file() -> Path:
    """Create the default envctl config file if it does not already exist."""
    config_path = get_default_config_path()

    if config_path.exists():
        raise ConfigError(f"Config file already exists: {config_path}")

    ensure_dir(config_path.parent)
    write_json_atomic(
        config_path,
        {
            "vault_dir": to_tilde_path(get_default_vault_dir()),
            "env_filename": get_default_env_filename(),
        },
    )
    ensure_private_file_permissions(config_path)

    return config_path
