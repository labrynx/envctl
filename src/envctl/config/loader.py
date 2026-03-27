"""Load and validate configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envctl.config.defaults import (
    get_default_config_path,
    get_default_env_filename,
    get_default_metadata_filename,
    get_default_vault_dir,
)
from envctl.errors import ConfigError
from envctl.models import AppConfig

SUPPORTED_KEYS = {"vault_dir", "env_filename"}


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file and return its parsed object."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON config: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read config file: {path}") from exc


def load_config() -> AppConfig:
    """Resolve the application configuration.

    v1 supports JSON only.

    TODO(v1.1):
    - accept YAML config files in addition to JSON
    - support config format auto-detection by extension
    - consider an explicit `envctl config init` bootstrap command
    """
    config_path = get_default_config_path()
    raw: dict[str, Any] = {}

    if config_path.exists():
        raw = _load_json(config_path)
        unknown = set(raw.keys()) - SUPPORTED_KEYS
        if unknown:
            keys = ", ".join(sorted(unknown))
            raise ConfigError(f"Unsupported config key(s): {keys}")

    vault_dir = Path(raw.get("vault_dir", get_default_vault_dir())).expanduser().resolve()
    env_filename = str(raw.get("env_filename", get_default_env_filename())).strip()

    if not env_filename:
        raise ConfigError("env_filename cannot be empty")
    if "/" in env_filename:
        raise ConfigError("env_filename must be a file name, not a path")

    return AppConfig(
        config_path=config_path,
        vault_dir=vault_dir,
        env_filename=env_filename,
        metadata_filename=get_default_metadata_filename(),
    )
