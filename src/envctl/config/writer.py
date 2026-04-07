"""Config file writer helpers."""

from __future__ import annotations

from pathlib import Path

from envctl.config.defaults import (
    get_default_config_path,
    get_default_contract_filename,
    get_default_env_filename,
    get_default_vault_dir,
)
from envctl.constants import DEFAULT_PROFILE
from envctl.domain.error_diagnostics import ConfigDiagnostics
from envctl.domain.runtime import RuntimeMode
from envctl.errors import ConfigError
from envctl.utils.atomic import write_json_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.tilde import to_tilde_path


def write_default_config_file() -> Path:
    """Create the default envctl config file if it does not exist."""
    config_path = get_default_config_path()

    if config_path.exists():
        raise ConfigError(
            f"Config file already exists: {config_path}",
            diagnostics=ConfigDiagnostics(
                category="config_file_exists",
                path=config_path,
                suggested_actions=("edit existing config.json",),
            ),
        )

    ensure_dir(config_path.parent)
    write_json_atomic(
        config_path,
        {
            "vault_dir": to_tilde_path(get_default_vault_dir()),
            "env_filename": get_default_env_filename(),
            "contract_filename": get_default_contract_filename(),
            "runtime_mode": RuntimeMode.LOCAL.value,
            "default_profile": DEFAULT_PROFILE,
            "encryption": {"enabled": False, "strict": False},
        },
    )
    return config_path
